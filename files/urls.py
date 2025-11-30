from django.urls import path
from . import views

app_name = 'files'

urlpatterns = [
    path('', views.list_view, name='list'),
    path('upload/', views.upload_view, name='upload'),
    path('download/<int:pk>/', views.download_view, name='download'),
    path('rename/<int:pk>/', views.rename_view, name='rename'),
    path('delete/<int:pk>/', views.delete_view, name='delete'),
    path('search/', views.search_view, name='search'),
    path('insights/<int:pk>/', views.insights_view, name='insights'),
    path('analytics/', views.analytics_page, name='analytics'),
]
