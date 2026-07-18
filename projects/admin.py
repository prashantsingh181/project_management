from django.contrib import admin

from .models import Membership, Project, Tag


# Register your models here.
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "is_archived")


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "project", "role")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "project")
