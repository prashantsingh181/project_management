from rest_framework import serializers

from .models import Comment, Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            "id",
            "project",
            "title",
            "description",
            "status",
            "priority",
            "position",
            "due_date",
            "assignees",
            "tags",
            "created_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "created_by",
            "created_at",
            "updated_at",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance is not None:
            self.fields["project"].read_only = True
        else:
            self.fields["status"].read_only = True

    def validate_project(self, project):
        request = self.context["request"]
        user = request.user
        if not project.memberships.filter(user=user).exists():
            raise serializers.ValidationError("You are not a member of this project.")

        return project

    def validate_status_transition(self, old_status, new_status):
        if old_status == Task.Status.TODO and new_status != Task.Status.IN_PROGRESS:
            raise serializers.ValidationError(
                {"status": "From 'todo', task status can be set to 'in progress' only"}
            )
        elif old_status == Task.Status.IN_PROGRESS and new_status not in [
            Task.Status.TODO,
            Task.Status.DONE,
        ]:
            raise serializers.ValidationError(
                {"status": "From 'in progress', task status can be set to 'todo' or 'done' only"}
            )
        elif old_status == Task.Status.DONE and new_status != Task.Status.IN_PROGRESS:
            raise serializers.ValidationError(
                {"status": "From 'done', task status can be set to 'in progress' only"}
            )

    def validate(self, attrs):
        project = attrs.get("project", getattr(self.instance, "project", None))
        old_status = getattr(self.instance, "status", None)
        new_status = attrs.get("status", old_status)

        if old_status != new_status:
            self.validate_status_transition(old_status, new_status)

        for user in attrs.get("assignees", []):
            if not project.memberships.filter(user=user).exists():
                raise serializers.ValidationError(
                    {"assignees": "Assignee is not a member of project."}
                )

        for tag in attrs.get("tags", []):
            if tag.project_id != project.id:
                raise serializers.ValidationError({"tags": "Tag does not belong to this project."})

        return attrs


class TaskCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("body", "author", "id", "created_at")
        read_only_fields = ("author", "created_at")
