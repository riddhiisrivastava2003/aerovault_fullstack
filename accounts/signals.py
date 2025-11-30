from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from adminpanel.models import ActivityLog

@receiver(user_logged_in)
def on_login(sender, user, request, **kwargs):
    ActivityLog.objects.create(user=user, action='login', details=f'IP: {request.META.get("REMOTE_ADDR") or "unknown"}')

@receiver(user_logged_out)
def on_logout(sender, user, request, **kwargs):
    ActivityLog.objects.create(user=user, action='logout', details=f'IP: {request.META.get("REMOTE_ADDR") or "unknown"}')
