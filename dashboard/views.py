from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from files.models import File
from django.db.models import Count, Sum


@login_required
def dashboard_view(request):
    user = request.user
    total_files = File.objects.filter(owner=user).count()
    recent = File.objects.filter(owner=user).order_by('-uploaded_on')[:6]
    storage = File.objects.filter(owner=user).aggregate(total=Sum('size'))['total'] or 0

    # cloud distribution (counts per stored_cloud)
    cloud_qs = File.objects.filter(owner=user).values('stored_cloud').annotate(count=Count('id')).order_by('-count')
    cloud_distribution = {row['stored_cloud']: row['count'] for row in cloud_qs}

    # file type distribution
    type_qs = File.objects.filter(owner=user).values('file_type').annotate(count=Count('id')).order_by('-count')
    type_distribution = {row['file_type'] or 'unknown': row['count'] for row in type_qs}

    context = {
        'total_files': total_files,
        'recent': recent,
        'storage': storage,
        'cloud_distribution': cloud_distribution,
        'type_distribution': type_distribution,
    }
    return render(request, 'dashboard/dashboard.html', context)
