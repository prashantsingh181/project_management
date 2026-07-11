from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models

from projects.models import Project, Tag


class Task(models.Model):
    class Status(models.TextChoices):
        TODO = "todo", "To Do"
        IN_PROGRESS = "in_progress", "In Progress"
        DONE = "done", "Done"

    class Priority(models.TextChoices):
        HIGHEST = "highest", "Highest"
        HIGH = "high", "High"
        MEDIUM = "medium", "Medium"
        LOW = "low", "Low"
        LOWEST = "lowest", "Lowest"

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    assignees = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="tasks", blank=True)
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.TODO)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    tags = models.ManyToManyField(Tag, related_name="tasks", blank=True)
    position = models.IntegerField(default=0)
    due_date = models.DateField(blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="created_tasks", on_delete=models.PROTECT
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} task of {self.project.name} project"


class Comment(models.Model):
    task = models.ForeignKey(Task, related_name="comments", on_delete=models.CASCADE)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="comments", on_delete=models.SET_NULL, null=True
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.email if self.author else 'Anonymous User'}'s comment on {self.task.title} task"


class Attachment(models.Model):
    task = models.ForeignKey(Task, related_name="attachments", on_delete=models.CASCADE)
    upload = models.FileField(
        upload_to="attachments/",
        validators=(
            FileExtensionValidator(
                allowed_extensions=("pdf", "docx", "doc", "png", "jpg", "jpeg", "webp", "avif")
            ),
        ),
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="attachments", on_delete=models.SET_NULL, null=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.uploaded_by.email if self.uploaded_by else 'Anonymous User'}'s upload on {self.task.title} task"
