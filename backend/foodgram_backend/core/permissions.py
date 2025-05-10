from rest_framework.permissions import IsAuthenticated, BasePermission


class IsAuthenticatedBanned(IsAuthenticated):
    """
    Разрешение проверяет, что пользователь аавторизирован и не в бане
    """
    def has_permission(self, request, view):
        is_authenticated = super().has_permission(request, view)
        return is_authenticated and request.user.is_active


class AuthorPermission(BasePermission):
    """
    Проверка, что пользвоатель автор объекта или админ
    """
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user or obj.author.is_admin
