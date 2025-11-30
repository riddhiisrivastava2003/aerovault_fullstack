from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
from files.models import File
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import os


class Command(BaseCommand):
    help = 'Regenerate thumbnails for image files missing thumbnails.'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=None, help='Max files to process')
        parser.add_argument('--force', action='store_true', help='Regenerate even if thumbnail exists')

    def handle(self, *args, **options):
        qs = File.objects.all().order_by('id')
        limit = options.get('limit')
        force = options.get('force', False)
        processed = 0

        if limit:
            self.stdout.write(f'Processing up to {limit} files')

        for f in qs:
            if not force and getattr(f, 'thumbnail', None):
                continue

            # try to access the file path
            try:
                file_path = f.file.path
            except Exception as e:
                self.stderr.write(f'Skipping id={f.id}: cannot access file path ({e})')
                continue

            # ensure file exists and is an image
            try:
                img = Image.open(file_path)
                img = img.convert('RGB')
            except Exception as e:
                self.stdout.write(f'Skipping id={f.id}: not an image or cannot open ({e})')
                continue

            try:
                img.thumbnail((200, 200))
                thumb_io = BytesIO()
                img.save(thumb_io, format='JPEG', quality=85)
                thumb_name = f'thumb_{os.path.basename(file_path)}.jpg'

                # save to model field
                f.thumbnail.save(thumb_name, ContentFile(thumb_io.getvalue()), save=True)
                processed += 1
                self.stdout.write(self.style.SUCCESS(f'Generated thumbnail for id={f.id} -> {thumb_name}'))
            except Exception as e:
                self.stderr.write(f'Failed to generate thumbnail for id={f.id}: {e}')

            if limit and processed >= limit:
                break

        self.stdout.write(self.style.SUCCESS(f'Done. Processed: {processed}'))
