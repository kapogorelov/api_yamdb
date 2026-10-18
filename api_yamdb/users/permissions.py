from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Доступ только для администраторов и суперпользователей."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (request.user.is_admin or request.user.is_superuser)
        )


class IsAdminOrReadOnly(IsAdmin):
    """Чтение для всех, запись только для администраторов."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or super().has_permission(request, view)
        )
