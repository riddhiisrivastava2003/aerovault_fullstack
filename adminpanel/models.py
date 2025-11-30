from django.db import models

# Placeholder models for adminpanel
class SystemLog(models.Model):
    action = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} @ {self.created_on}"


class ActivityLog(models.Model):
    user = models.ForeignKey('accounts.User', null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=255)
    details = models.TextField(blank=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return f"{self.user} - {self.action} @ {self.created_on}"


class AdminConfig(models.Model):
    """Simple config model for admin-controlled settings like default cloud and pricing."""
    default_cloud = models.CharField(max_length=50, default='Azure')
    aws_price_per_gb = models.FloatField(default=0.023)
    azure_price_per_gb = models.FloatField(default=0.024)
    gcp_price_per_gb = models.FloatField(default=0.020)

    def __str__(self):
        return f"AdminConfig(default={self.default_cloud})"
