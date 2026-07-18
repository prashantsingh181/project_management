from rest_framework import permissions

from projects.models import Membership


class IsOwnerOrAdminOrReadonly(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user is not None and user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if self.has_permission(request, view) and request.method in permissions.SAFE_METHODS:
            return True
        memberships = Membership.objects.filter(
            project=obj, role__in=(Membership.Role.OWNER, Membership.Role.ADMIN)
        )
        admins_or_owner = [membership.user for membership in memberships]
        return request.user in admins_or_owner


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner
