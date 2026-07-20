from django.db import transaction
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from tasks.permissions import IsMember
from tasks.serializers import (
    AttachmentSerializer,
    TaskCommentSerializer,
    TaskMoveSerializer,
    TaskSerializer,
)
from tasks.throttles import AttachmentUploadThrottle, CommentCreationThrottle

from .models import Attachment, Task


class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = (IsMember,)
    serializer_class = TaskSerializer

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)

    filterset_fields = ("project", "status", "created_by")
    search_fields = ("title", "description", "priority")
    ordering_fields = ("created_at", "position")
    ordering = ("position",)

    def get_queryset(self):
        return Task.objects.filter(project__memberships__user=self.request.user)

    def perform_create(self, serializer):
        return serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.instance._actor = self.request.user
        return serializer.save()

    @action(detail=False, methods=["patch"])
    def bulk(self, request, *args, **kwargs):
        if not isinstance(request.data, list):
            return Response(
                {"error": "Expected a list of items"}, status=status.HTTP_400_BAD_REQUEST
            )

        results = []
        with transaction.atomic():
            for item in request.data:
                task_id = item.get("id")
                if task_id is None:
                    return Response(
                        {"error": "Each item must include an 'id'."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                task = get_object_or_404(self.get_queryset(), pk=task_id)
                serializer = self.get_serializer(task, data=item, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.instance._actor = request.user
                serializer.save()
                results.append(serializer.data)

        return Response(results)

    @action(detail=True, methods=["get", "post"], throttle_classes=[CommentCreationThrottle])
    def comments(self, request, *args, **kwargs):
        task = self.get_object()
        if request.method == "GET":
            comments = task.comments.all()
            serializer = TaskCommentSerializer(comments, many=True)
            return Response(serializer.data)

        elif request.method == "POST":
            serializer = TaskCommentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(task=task, author=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def move(self, request, *args, **kwargs):
        task = self.get_object()
        serializer = TaskMoveSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get", "post"], throttle_classes=[AttachmentUploadThrottle])
    def attachment(self, request, *args, **kwargs):
        task = self.get_object()
        if request.method == "GET":
            attachments = Attachment.objects.filter(task=task)
            serializer = AttachmentSerializer(attachments, many=True)
            return Response(serializer.data)

        serializer = AttachmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(task=task, uploaded_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
