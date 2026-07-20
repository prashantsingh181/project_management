from rest_framework import serializers

from .models import Attachment, Comment, Task


class TaskBulkUpdateSerializer(serializers.ListSerializer):
    def update(self, instance, validated_data):
        instance_mapping = {obj.id: obj for obj in instance}

        updated_objects = []
        updated_fields = set()

        for item in validated_data:
            object_id = item.get("id")
            obj = instance_mapping.get(object_id)

            if obj:
                for attr, value in item.items():
                    setattr(obj, attr, value)
                    if attr != "id":
                        updated_fields.add(attr)
                updated_objects.append(obj)

        if updated_objects:
            self.child.Meta.model.objects.bulk_update(updated_objects, fields=list(updated_fields))

        return updated_objects


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

        list_serializer_class = TaskBulkUpdateSerializer

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


class TaskMoveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ("project", "title", "description", "status", "position", "priority")
        read_only_fields = ("project", "title", "description", "status", "priority")


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ("id", "upload", "uploaded_by", "uploaded_at", "task")
        read_only_fields = ("task", "uploaded_by", "uploaded_at")

    def validate_upload(self, file):
        max_mb = 2
        if file.size > max_mb * 1024 * 1024:
            raise serializers.ValidationError({"upload": "File must be under {max_mb} MB."})
        return file
