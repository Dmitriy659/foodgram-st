import io

from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Recipe, Favourite, ShoppingCart, RecipeIngredient
from .permissions import AuthorPermission
from .serializers import RecipeSerializer
from .base import RecipeMinSerializer


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


class BaseRecipeActionView(APIView):
    permission_classes = [IsAuthenticated]
    model = None
    serializer_class = RecipeMinSerializer
    not_found_message = "Рецепт не найден."

    def post(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        if self.model.objects.filter(author=request.user, recipe=recipe).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        self.model.objects.create(author=request.user, recipe=recipe)
        data = self.serializer_class(recipe, context={'request': request}).data
        return Response(data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        inst = self.model.objects.filter(author=request.user, recipe=recipe).first()
        if not inst:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        inst.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavouritesView(BaseRecipeActionView):
    model = Favourite
    not_found_message = "Этого рецепта нет в избранном."


class ShoppingCartView(BaseRecipeActionView):
    model = ShoppingCart
    not_found_message = "Этого рецепта нет в корзине."


class DownloadShoppingCart(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        author = self.request.user
        ingredients_dict = {}

        recipes_cart = ShoppingCart.objects.filter(author=author)

        for recipe_cart in recipes_cart:
            recipe = recipe_cart.recipe
            recipe_ingredients = RecipeIngredient.objects.filter(recipe=recipe)
            for recipe_ingredient in recipe_ingredients:
                ingredient = recipe_ingredient.ingredient
                measure_unit = ingredient.measurement_unit
                amount = recipe_ingredient.amount
                ingredient_name = ingredient.name

                if ingredient_name in ingredients_dict:
                    ingredients_dict[ingredient_name]["amount"] += amount
                else:
                    ingredients_dict[ingredient_name] = {
                        "amount": amount,
                        "measure_unit": measure_unit,
                    }

        buffer = io.StringIO()
        buffer.write("Список ингредиентов:")

        for ingredient, details in ingredients_dict.items():
            amount = details["amount"]
            measure_unit = details["measure_unit"]
            buffer.write(f"\n{ingredient}: {amount} {measure_unit}")

        buffer.seek(0)
        response = Response(buffer.getvalue(), content_type="text/plain; charset=utf-8")
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response
