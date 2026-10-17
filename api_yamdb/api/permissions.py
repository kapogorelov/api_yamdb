from rest_framework import permissions


class IsAdminModeratorOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return (
            obj.author == request.user
            or getattr(request.user, 'is_moderator', False)
            or getattr(request.user, 'is_admin', False)
            or request.user.is_superuser
        )
