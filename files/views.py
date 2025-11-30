from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import File
from django.conf import settings
from django.http import HttpResponse, Http404

from django import forms
from adminpanel.models import ActivityLog
from django.utils import timezone
from django.db import models
from django.db.models import Count, Sum
import os
from PIL import Image
try:
    from cryptography.fernet import Fernet
    FERNET_AVAILABLE = True
except Exception:
    FERNET_AVAILABLE = False


def _auto_select_cloud(filename, size):
    """Simple heuristic to pick a cloud (simulated AI).
    - Images -> AWS
    - Large files (>100MB) -> GCP
    - Otherwise -> Azure
    """
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    image_exts = {'jpg','jpeg','png','gif','bmp','webp','heic'}
    if ext in image_exts:
        return 'AWS'
    if size and size > 100 * 1024 * 1024:
        return 'GCP'
    return 'Azure'

class UploadForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['file', 'tags']


class MultiUploadForm(forms.Form):
    # Use a normal ClearableFileInput instance here; the template provides the
    # `multiple` attribute on the `<input>` so we avoid widget-level validation
    # that forbids multiple selection.
    files = forms.FileField(widget=forms.ClearableFileInput(), required=False)
    tags = forms.CharField(required=False)

@login_required
def upload_view(request):
    # support multi-file upload
    if request.method == 'POST':
        form = MultiUploadForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('files')
            tags = form.cleaned_data.get('tags', '')
            created = []
            auto_cloud = request.POST.get('auto_cloud') in ('on','true','1')
            do_encrypt = request.POST.get('encrypt') in ('on','true','1')
            for up in files:
                # Prepare file record (we may replace file contents if encrypted)
                f = File(owner=request.user, tags=tags, uploaded_on=timezone.now())
                if '.' in up.name:
                    f.file_type = up.name.rsplit('.',1)[-1].lower()
                f.name = up.name
                f.size = up.size

                # Handle encryption if requested and available
                if do_encrypt:
                    if not FERNET_AVAILABLE:
                        # skip encryption if library is not available
                        try:
                            ActivityLog.objects.create(user=request.user, action='encrypt_failed', details=f'cryptography missing for {up.name}')
                        except Exception:
                            pass
                    else:
                        key = Fernet.generate_key()
                        f.encrypted = True
                        f.encryption_key = key.decode()
                        fer = Fernet(key)
                        raw = up.read()
                        encrypted = fer.encrypt(raw)
                        # create a ContentFile for the encrypted bytes and set a new filename
                        enc_name = os.path.splitext(up.name)[0] + '.enc'
                        up = ContentFile(encrypted, name=enc_name)
                        f.name = enc_name
                        f.size = len(encrypted)

                # Auto cloud selection
                if auto_cloud:
                    f.stored_cloud = _auto_select_cloud(f.name, f.size)

                # Save file field and model
                f.file = up
                f.save()
                created.append(f)
                try:
                    ActivityLog.objects.create(user=request.user, action='upload', details=f'File:{f.name} size:{f.size}')
                except Exception:
                    pass
            return redirect('files:list')
    else:
        form = MultiUploadForm()
    return render(request, 'files/upload.html', {'form': form})

@login_required
def list_view(request):
    files = File.objects.filter(owner=request.user).order_by('-uploaded_on')
    return render(request, 'files/list.html', {'files': files})


@login_required
def rename_view(request, pk):
    obj = get_object_or_404(File, pk=pk, owner=request.user)
    if request.method == 'POST':
        new = request.POST.get('name')
        if new:
            old = obj.name
            obj.name = new
            obj.save()
            try:
                ActivityLog.objects.create(user=request.user, action='rename', details=f'{old} -> {new}')
            except Exception:
                pass
            return redirect('files:list')
    return render(request, 'files/rename.html', {'file': obj})


@login_required
def delete_view(request, pk):
    obj = get_object_or_404(File, pk=pk, owner=request.user)
    if request.method == 'POST':
        try:
            ActivityLog.objects.create(user=request.user, action='delete', details=f'File:{obj.name} id:{obj.pk}')
        except Exception:
            pass
        obj.file.delete(save=False)
        obj.delete()
        return redirect('files:list')
    return render(request, 'files/confirm_delete.html', {'file': obj})

@login_required
def download_view(request, pk):
    obj = get_object_or_404(File, pk=pk, owner=request.user)
    file_field = obj.file
    if not file_field:
        raise Http404
    response = HttpResponse(file_field, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{obj.name}"'
    try:
        ActivityLog.objects.create(user=request.user, action='download', details=f'File:{obj.name} id:{obj.pk}')
    except Exception:
        pass
    return response


@login_required
def search_view(request):
    q = request.GET.get('q','').strip()
    ftype = request.GET.get('type','')
    cloud = request.GET.get('cloud','')
    qs = File.objects.filter(owner=request.user)
    if q:
        qs = qs.filter(models.Q(name__icontains=q) | models.Q(tags__icontains=q))
    if ftype:
        qs = qs.filter(file_type=ftype)
    if cloud:
        qs = qs.filter(stored_cloud=cloud)
    # common file extensions to show in the type selector
    ALL_FILE_TYPES = [
        'pdf','doc','docx','xls','xlsx','ppt','pptx','txt','csv',
        'jpg','jpeg','png','gif','bmp','webp','heic',
        'mp4','mov','avi','mkv','webm','mp3','wav','ogg',
        'zip','rar','7z','tar','gz','iso','apk','exe',
        'html','css','js','json','xml','svg','md','rtf'
    ]
    existing_types = File.objects.filter(owner=request.user).values_list('file_type', flat=True).distinct()
    # merge and sort unique types, preferring existing types first
    merged = list(dict.fromkeys([t for t in existing_types if t] + [t for t in ALL_FILE_TYPES if t]))
    types = merged
    clouds = list(File.objects.filter(owner=request.user).values_list('stored_cloud', flat=True).distinct())
    return render(request, 'files/search.html', {'results': qs, 'types': types, 'clouds': clouds})


@login_required
def insights_view(request, pk):
    file = get_object_or_404(File, pk=pk, owner=request.user)
    # Basic insights: file type, size, uploaded_on, owner's stats
    owner_total_files = File.objects.filter(owner=file.owner).count()
    owner_total_storage = File.objects.filter(owner=file.owner).aggregate(total=Sum('size'))['total'] or 0
    same_type_count = File.objects.filter(owner=file.owner, file_type=file.file_type).count()

    insights = {
        'file_id': file.pk,
        'name': file.name,
        'file_type': file.file_type,
        'size': file.size,
        'uploaded_on': file.uploaded_on,
        'owner_total_files': owner_total_files,
        'owner_total_storage': owner_total_storage,
        'same_type_count': same_type_count,
    }

    return render(request, 'files/insights.html', {'insights': insights, 'file': file})


@login_required
def analytics_page(request):
    # Simple analytics page that aggregates files per user and per type
    files_by_user = File.objects.values('owner__username').annotate(count=Count('id')).order_by('-count')[:10]
    files_by_type = File.objects.values('file_type').annotate(count=Count('id')).order_by('-count')

    context = {
        'files_by_user': list(files_by_user),
        'files_by_type': list(files_by_type),
    }
    return render(request, 'files/analytics.html', context)
