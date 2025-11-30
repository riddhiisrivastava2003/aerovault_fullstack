from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('adminpanel', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('default_cloud', models.CharField(default='Azure', max_length=50)),
                ('aws_price_per_gb', models.FloatField(default=0.023)),
                ('azure_price_per_gb', models.FloatField(default=0.024)),
                ('gcp_price_per_gb', models.FloatField(default=0.02)),
            ],
        ),
    ]
