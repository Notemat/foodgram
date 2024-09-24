from rest_framework import permissions


class PostOrReadOnly(permissions.BasePermission):
    """Пермишен разрешающий безопасные методы и метод POST."""

    def has_permission(self, request, view):
        method = request.method
        return method in permissions.SAFE_METHODS or method == "POST"
