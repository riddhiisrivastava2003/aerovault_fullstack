from django.http import JsonResponse
from django.db.models import Count, Sum
from files.models import File
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.db.models.functions import TruncDay

from django.utils import timezone
from datetime import timedelta

# ... (other imports)

@require_GET
@login_required
def upload_history(request):
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    qs = File.objects.filter(
        owner=request.user,
        uploaded_on__gte=start_date,
        uploaded_on__lte=end_date
    ).annotate(day=TruncDay('uploaded_on')).values('day').annotate(count=Count('id')).order_by('day')
    data = [{'day': r['day'].date().isoformat(), 'count': r['count']} for r in qs]
    return JsonResponse({'data': data})

@require_GET
@login_required
def cloud_distribution(request):
    qs = File.objects.filter(owner=request.user).values('stored_cloud').annotate(count=Count('id'))
    data = [{'cloud': r['stored_cloud'], 'count': r['count']} for r in qs]
    return JsonResponse({'data': data})

@require_GET
@login_required
def filetype_distribution(request):
    qs = File.objects.filter(owner=request.user).values('file_type').annotate(count=Count('id'))
    data = [{'type': r['file_type'] or 'unknown', 'count': r['count']} for r in qs]
    return JsonResponse({'data': data})


@require_GET
@login_required
def storage_usage(request):
    # total storage used per file type for the user
    qs = File.objects.filter(owner=request.user).values('file_type').annotate(total=Sum('size')).order_by('-total')
    data = [{'type': r['file_type'] or 'unknown', 'total': r['total'] or 0} for r in qs]
    return JsonResponse({'data': data})
