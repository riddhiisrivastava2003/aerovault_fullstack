from django.contrib import admin
from .models import File

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'file_type', 'size', 'uploaded_on', 'stored_cloud')
    search_fields = ('name', 'tags')
