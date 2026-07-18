from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from projects.permissions import IsOwner, IsOwnerOrAdminOrReadonly
from users.models import User

from .models import Membership, Project
from .serializers import (
    MembershipUpdateSerializer,
    ProjectMembershipSerializer,
    ProjectSerializer,
)


class ProjectViewset(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = (IsOwnerOrAdminOrReadonly,)

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(memberships__user=user, is_archived=False)

    def perform_create(self, serializer):
        with transaction.atomic():
            instance = serializer.save(owner=self.request.user)
            Membership.objects.create(
                project=instance, user=instance.owner, role=Membership.Role.OWNER
            )
        return instance

    def destroy(self, request, *args, **kwargs):
        project = self.get_object()
        if request.user != project.owner:
            return Response(
                {"message": "Only Owner can delete the project."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["get", "post"],
        permission_classes=[IsOwnerOrAdminOrReadonly],
        url_path="members",
    )
    def members_list(self, request, *args, **kwargs):
        project = self.get_object()
        if request.method == "GET":
            memberships = Membership.objects.select_related("user").filter(project=project)
            serializer = ProjectMembershipSerializer(memberships, many=True)
            return Response(serializer.data)

        elif request.method == "POST":
            serializer = ProjectMembershipSerializer(data=request.data)
            if serializer.is_valid():
                existing_membership = Membership.objects.filter(
                    user=serializer.validated_data["user"], project=project
                )
                if existing_membership.exists():
                    return Response(
                        {"message": "A membership for this user already exists."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                else:
                    serializer.save(project=project)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=["patch", "delete"],
        permission_classes=[IsOwner],
        url_path=r"members/(?P<user_id>\d+)",
    )
    def members_detail(self, request, user_id=None, *args, **kwargs):
        project = self.get_object()
        user = get_object_or_404(User, id=user_id)
        membership = get_object_or_404(Membership, project=project, user=user)

        if request.method == "PATCH":
            if user == request.user:
                return Response(
                    {"message": "Cannot change self role"}, status=status.HTTP_400_BAD_REQUEST
                )
            serializer = MembershipUpdateSerializer(membership, data=request.data)
            if serializer.is_valid():
                if serializer.validated_data["role"] == Membership.Role.OWNER:
                    owner_membership = Membership.objects.get(
                        project=project, role=Membership.Role.OWNER
                    )
                    owner_membership.role = Membership.Role.ADMIN
                    owner_membership.save()
                    project.owner = user
                    project.save()
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == "DELETE":
            if membership.role == Membership.Role.OWNER:
                return Response(
                    {"message": "Cannot remove the owner"}, status=status.HTTP_400_BAD_REQUEST
                )
            membership.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
