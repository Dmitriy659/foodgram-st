from rest_framework.permissions import BasePermission, SAFE_METHODS


class AuthorOrReadPermission(BasePermission):
    """
    Проверка, что пользвоатель автор объекта или админ
    """
    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or obj.author == request.user)
