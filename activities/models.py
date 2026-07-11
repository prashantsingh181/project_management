from django.conf import settings
from django.db import models

from projects.models import Project


class ActivityLog(models.Model):
    project = models.ForeignKey(Project, related_name="activity_logs", on_delete=models.CASCADE)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="activity_logs", on_delete=models.SET_NULL, null=True
    )
    verb = models.CharField(max_length=100)
    target = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.actor.email if self.actor else 'Anonymous User'} performed {self.verb} on {self.target}"
