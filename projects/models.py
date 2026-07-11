from django.conf import settings
from django.db import models


class Project(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="projects", on_delete=models.PROTECT
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} project by {self.owner.email}"


class Membership(models.Model):
    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"
        MEMBER = "member", "Member"

    project = models.ForeignKey(Project, related_name="memberships", on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="memberships", on_delete=models.CASCADE
    )
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=("user", "project"), name="unique_project_user"),
        )

    def __str__(self):
        return f"{self.user.email}{(self.role)} membership in {self.project.name} project"


class Tag(models.Model):
    project = models.ForeignKey(Project, related_name="tags", on_delete=models.CASCADE)
    name = models.CharField(max_length=25)
    description = models.TextField(blank=True)

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=("project", "name"), name="unique_project_tag"),
        )

    def __str__(self):
        return f"{self.name} tag of {self.project.name} project"
