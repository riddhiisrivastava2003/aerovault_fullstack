from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0002_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='encrypted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='file',
            name='encryption_key',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
