from django.urls import path
from . import views
from . import auth_views

app_name = 'adminpanel'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', auth_views.admin_login, name='login'),
    path('logout/', auth_views.admin_logout, name='logout'),
    path('users/', views.users_list, name='users'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/edit/<int:pk>/', views.user_edit, name='user_edit'),
    path('users/delete/<int:pk>/', views.user_delete, name='user_delete'),
    path('files/', views.files_list, name='files'),
    path('files/download/<int:pk>/', views.admin_file_download, name='admin_file_download'),
    path('files/delete/<int:pk>/', views.admin_file_delete, name='admin_file_delete'),
    path('files/details/<int:pk>/', views.admin_file_details, name='admin_file_details'),
    path('logs/', views.logs_list, name='logs'),
    path('cloud-settings/', views.cloud_settings, name='cloud_settings'),
    path('system-monitor/', views.system_monitor, name='system_monitor'),
]
