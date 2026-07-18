from rest_framework import permissions


class IsMember(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user is not None and user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        member_query = obj.project.memberships.filter(user=user)
        return member_query.exists()
