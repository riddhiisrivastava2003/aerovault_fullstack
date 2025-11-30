from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from adminpanel.models import ActivityLog, SystemLog
from accounts.models import User
from files.models import File
from .models import AdminConfig
from django import forms
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Count
from django.db import ProgrammingError, OperationalError
from django.http import HttpResponse, Http404 # Import for file downloads
from .forms import UserAdminForm # Import the new form


@staff_member_required
def dashboard(request):
    total_users = User.objects.count()
    total_files = File.objects.count()
    total_storage = File.objects.aggregate(total=Sum('size'))['total'] or 0
    # cloud distribution
    cloud_qs = File.objects.values('stored_cloud').annotate(count=Count('id'))
    cloud_distribution = {r['stored_cloud']: r['count'] for r in cloud_qs}
    # cost estimation using AdminConfig prices
    # AdminConfig table may not exist yet (migrations not applied).
    # Wrap DB access so the dashboard can still render with safe defaults.
    try:
        cfg = AdminConfig.objects.first()
        if not cfg:
            try:
                cfg = AdminConfig.objects.create()
            except (ProgrammingError, OperationalError):
                cfg = None
    except (ProgrammingError, OperationalError):
        cfg = None

    if cfg is None:
        # fallback configuration when DB table is absent
        class _Cfg:
            default_cloud = 'local'
            aws_price_per_gb = 0.0
            azure_price_per_gb = 0.0
            gcp_price_per_gb = 0.0

        cfg = _Cfg()
    cost_estimate = 0.0
    # estimate cost based on storage distribution per cloud using simple per-GB price
    for cloud, count in cloud_distribution.items():
        # approximate storage share by count * average file size
        avg_size = File.objects.filter(stored_cloud=cloud).aggregate(avg=Sum('size'))['avg'] or 0
        gb = (avg_size / (1024*1024*1024))
        price = cfg.azure_price_per_gb
        if cloud and cloud.upper().startswith('AWS'):
            price = cfg.aws_price_per_gb
        if cloud and cloud.upper().startswith('GCP'):
            price = cfg.gcp_price_per_gb
        cost_estimate += gb * price

    recent_logs = ActivityLog.objects.all()[:20]
    alerts = SystemLog.objects.filter(action__icontains='alert').order_by('-created_on')[:10]
    context = {
        'total_users': total_users,
        'total_files': total_files,
        'total_storage': total_storage,
        'cloud_distribution': cloud_distribution,
        'cost_estimate': round(cost_estimate, 4),
        'recent_logs': recent_logs,
        'alerts': alerts,
    }
    return render(request, 'adminpanel/dashboard.html', context)


class AdminConfigForm(forms.ModelForm):
    class Meta:
        model = AdminConfig
        fields = ('default_cloud','aws_price_per_gb','azure_price_per_gb','gcp_price_per_gb')


@staff_member_required
def cloud_settings(request):
    cfg = AdminConfig.objects.first()
    if not cfg:
        cfg = AdminConfig.objects.create()
    if request.method == 'POST':
        form = AdminConfigForm(request.POST, instance=cfg)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cloud settings updated')
            return redirect('adminpanel:dashboard')
    else:
        form = AdminConfigForm(instance=cfg)
    return render(request, 'adminpanel/cloud_settings.html', {'form': form})


@staff_member_required
def system_monitor(request):
    # display recent system logs and simple counts
    errors = SystemLog.objects.filter(action__icontains='error').order_by('-created_on')[:50]
    recent_activity = ActivityLog.objects.all()[:50]
    return render(request, 'adminpanel/system_monitor.html', {'errors': errors, 'recent_activity': recent_activity})


@staff_member_required
def users_list(request):
    users = User.objects.all().order_by('username')
    return render(request, 'adminpanel/users.html', {'users': users})

@staff_member_required
def user_create(request):
    if request.method == 'POST':
        form = UserAdminForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User {user.username} created successfully.')
            return redirect('adminpanel:users')
    else:
        form = UserAdminForm()
    return render(request, 'adminpanel/user_form.html', {'form': form, 'title': 'Create User'})

@staff_member_required
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserAdminForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User {user.username} updated successfully.')
            return redirect('adminpanel:users')
    else:
        form = UserAdminForm(instance=user)
    return render(request, 'adminpanel/user_form.html', {'form': form, 'title': 'Edit User', 'user': user})

@staff_member_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, f'User {user.username} deleted successfully.')
        return redirect('adminpanel:users')
    return render(request, 'adminpanel/user_confirm_delete.html', {'user': user})


@staff_member_required
def files_list(request):
    files = File.objects.select_related('owner').all().order_by('-uploaded_on')
    return render(request, 'adminpanel/files.html', {'files': files})

@staff_member_required
def admin_file_download(request, pk):
    file_obj = get_object_or_404(File, pk=pk)
    file_field = file_obj.file
    if not file_field:
        raise Http404

    response = HttpResponse(file_field, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{file_obj.name}"'
    try:
        ActivityLog.objects.create(user=request.user, action='admin_download', details=f'File:{file_obj.name} id:{file_obj.pk} by admin {request.user.username}')
    except Exception:
        pass
    return response

@staff_member_required
def admin_file_delete(request, pk):
    file_obj = get_object_or_404(File, pk=pk)
    if request.method == 'POST':
        try:
            ActivityLog.objects.create(user=request.user, action='admin_delete', details=f'File:{file_obj.name} id:{file_obj.pk} by admin {request.user.username}')
        except Exception:
            pass
        file_obj.file.delete(save=False) # Delete the physical file
        file_obj.delete() # Delete the database record
        messages.success(request, f'File "{file_obj.name}" deleted successfully.')
        return redirect('adminpanel:files')
    return render(request, 'adminpanel/admin_file_confirm_delete.html', {'file_obj': file_obj})

@staff_member_required
def admin_file_details(request, pk):
    file_obj = get_object_or_404(File, pk=pk)
    return render(request, 'adminpanel/admin_file_details.html', {'file_obj': file_obj})


@staff_member_required
def logs_list(request):
    logs = ActivityLog.objects.all()
    return render(request, 'adminpanel/logs.html', {'logs': logs})
