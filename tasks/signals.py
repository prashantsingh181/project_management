from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from activities.models import ActivityLog

from .models import Task


@receiver(signal=pre_save, sender=Task)
def stash_previous_status(sender, instance, **kwargs):
    if not instance.pk:
        instance._previous_status = None
        return
    try:
        instance._previous_status = Task.objects.get(pk=instance.pk).status
    except Task.DoesNotExist:
        instance._previous_status = None


@receiver(signal=post_save, sender=Task)
def log_task_changes(sender, instance, created, **kwargs):
    old_status = getattr(instance, "_previous_status", None)
    if created:
        ActivityLog.objects.create(
            project=instance.project,
            actor=instance.created_by,
            verb="creation",
            target=f"Task {instance.id}",
        )
    elif old_status != instance.status:
        ActivityLog.objects.create(
            project=instance.project,
            actor=getattr(instance, "_actor", None),
            verb="status_change",
            target=f"Task {instance.id}: {old_status} -> {instance.status} ",
        )
