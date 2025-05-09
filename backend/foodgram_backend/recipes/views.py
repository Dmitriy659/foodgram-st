from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import MethodNotAllowed
from .models import Recipe
from .serializers import RecipeSerializer
from .permissions import AuthorPermission


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        return RecipeSerializer  # TODO добавить сериализаторы для каждого метода

    def get_permissions(self):
        if self.action in ("create",):
            return [IsAuthenticated()]
        elif self.action in ("list", "retrieve"):
            return [AllowAny()]
        elif self.action in ("partial_update", "destroy"):
            return [IsAuthenticated(), AuthorPermission()]
        raise MethodNotAllowed(f"Method {self.action} is not allowed")
