from rest_framework import serializers

from activities.models import ActivityLog


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = ("id", "project", "actor", "verb", "created_at")
