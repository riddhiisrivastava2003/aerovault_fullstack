from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('upload-history/', views.upload_history, name='upload_history'),
    path('cloud-distribution/', views.cloud_distribution, name='cloud_distribution'),
    path('filetype-distribution/', views.filetype_distribution, name='filetype_distribution'),
    path('storage_usage/', views.storage_usage, name='storage_usage'),
]
