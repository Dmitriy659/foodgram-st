from rest_framework import permissions


class AuthorPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method in ["PATCH", 'DELETE'] and obj.author == request.user
