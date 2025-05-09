from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response
from .models import Recipe, Favourite
from .serializers import RecipeSerializer, FavouriteSerializer
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


class FavouritesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, recipe_id):
        try:
            recipe = Recipe.objects.get(pk=recipe_id)
        except Recipe.DoesNotExist:
            return Response({"detail": "Рецепт не найден."}, status=status.HTTP_404_NOT_FOUND)

        if Favourite.objects.filter(author=request.user, recipe=recipe).exists():
            return Response({"detail": "Этот рецепт уже в избранном."}, status=status.HTTP_400_BAD_REQUEST)

        favourite = Favourite.objects.create(author=request.user, recipe=recipe)
        serializer = FavouriteSerializer(favourite, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        try:
            recipe = Recipe.objects.get(pk=recipe_id)
        except Recipe.DoesNotExist:
            return Response({"detail": "Такого рецепта нет."}, status=status.HTTP_404_NOT_FOUND)

        favourite = Favourite.objects.filter(author=request.user, recipe=recipe).first()
        if not favourite:
            return Response({"detail": "Такого рецепта нет в избранных."}, status=status.HTTP_400_BAD_REQUEST)

        favourite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
