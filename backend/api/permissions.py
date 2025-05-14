from rest_framework.permissions import BasePermission


class AuthorPermission(BasePermission):
    """
    Проверка, что пользвоатель автор объекта или админ
    """
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user or obj.author.is_admin
