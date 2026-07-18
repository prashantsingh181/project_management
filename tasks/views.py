from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from tasks.permissions import IsMember
from tasks.serializers import TaskCommentSerializer, TaskSerializer
from tasks.throttles import CommentCreationThrottle

from .models import Task


class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = (IsMember,)
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(project__memberships__user=self.request.user)

    def perform_create(self, serializer):
        return serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["get", "post"], throttle_classes=[CommentCreationThrottle])
    def comments(self, request):
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
