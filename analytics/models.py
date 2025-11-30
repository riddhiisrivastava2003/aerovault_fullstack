from django.db import models

# Placeholder models for analytics (expand later)
class AnalyticsEvent(models.Model):
    name = models.CharField(max_length=200)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
