from rest_framework import permissions


class IsAdminPermission(permissions.BasePermission):
    """Разрешения уровня `администратор`."""
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return (
                request.user.is_admin
                or request.user.is_superuser
            )
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return (
                request.user.is_admin
                or request.user.is_superuser
            )
        return False


class IsAuthorPermission(permissions.BasePermission):
    """Разрешения уровня `авторизированный пользователь`."""
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user