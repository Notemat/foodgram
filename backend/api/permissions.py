from rest_framework import permissions


class AuthorOrReadOnlyPermission(permissions.BasePermission):
    """Пермишен запрещающий небезопасные методы для всех, кроме авторов.."""

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )