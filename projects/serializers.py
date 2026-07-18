from rest_framework import serializers

from .models import Membership, Project


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ("id", "name", "description")


class ProjectMembershipSerializer(serializers.ModelSerializer):
    role = serializers.ReadOnlyField()

    class Meta:
        model = Membership
        fields = ("id", "user", "role")


class MembershipUpdateSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.id")

    class Meta:
        model = Membership
        fields = (
            "id",
            "role",
            "user",
        )
