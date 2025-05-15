from rest_framework.permissions import BasePermission, SAFE_METHODS


class AuthorPermission(BasePermission):
    """
    Проверка, что пользвоатель автор объекта или админ
    """
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class UserDataPermission(BasePermission):
    def has_permission(self, request, view):
        if view.action == "me":
            return request.user and request.user.is_authenticated
        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        cur_user = request.user
        return request.method in SAFE_METHODS or cur_user.is_authenticated and cur_user == obj
