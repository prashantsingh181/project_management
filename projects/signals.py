from django.db.models.signals import post_save
from django.dispatch import receiver

from activities.models import ActivityLog
from projects.models import Membership


@receiver(signal=post_save, sender=Membership)
def log_member_add(sender, instance, created, **kwargs):
    if created:
        ActivityLog.objects.create(
            project=instance.project,
            actor=getattr(instance, "_actor", None),
            verb="member_add",
            target=f"Project {instance.project.id}: Added Member {instance.user.id}",
        )
