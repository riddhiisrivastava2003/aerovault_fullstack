from django.db import models
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils.translation import gettext_lazy as _

from PIL import Image
import io
import os

class File(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='uploads/')
    thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True)
    encrypted = models.BooleanField(default=False)
    encryption_key = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50, blank=True)
    size = models.BigIntegerField(default=0)
    uploaded_on = models.DateTimeField(auto_now_add=True)
    stored_cloud = models.CharField(max_length=50, default='local')
    tags = models.CharField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        if self.file:
            self.size = self.file.size
            if not self.name:
                self.name = self.file.name
            # simple file type detection
            if '.' in self.file.name:
                self.file_type = self.file.name.rsplit('.', 1)[-1].lower()
        super().save(*args, **kwargs)

        # If uploaded file is an image, create a thumbnail
        try:
            img_types = ('jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp')
            if self.file and self.file_type in img_types:
                self.file.open()
                img = Image.open(self.file)
                img.convert('RGB')
                img.thumbnail((400, 300))
                thumb_io = io.BytesIO()
                img.save(thumb_io, format='JPEG', quality=80)
                thumb_name = os.path.splitext(os.path.basename(self.file.name))[0] + '_thumb.jpg'
                self.thumbnail.save(thumb_name, ContentFile(thumb_io.getvalue()), save=False)
                super().save(update_fields=['thumbnail'])
        except Exception:
            # fail silently for thumbnail generation
            pass

    def __str__(self):
        return f"{self.name} ({self.owner})"
