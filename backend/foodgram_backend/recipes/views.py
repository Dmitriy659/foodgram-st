import io

from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.urls.base import reverse
from rest_framework import viewsets, status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
import pyshorteners

from .models import Recipe, Favourite, ShoppingCart, RecipeIngredient
from .permissions import AuthorPermission
from .serializers import RecipeSerializer
from core.pagination import CustomPagination
from core.serializer import RecipeMinSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    serializer_class = RecipeSerializer

    def get_permissions(self):
        if self.action in ("create",):
            return [IsAuthenticated()]
        elif self.action in ("list", "retrieve", "get_link"):
            return [AllowAny()]
        elif self.action in ("partial_update", "destroy"):
            return [IsAuthenticated(), AuthorPermission()]
        raise MethodNotAllowed(f"Method {self.action} is not allowed")

    def get_queryset(self):
        queryset = Recipe.objects.all()


        is_favorited = self.request.query_params.get('is_favorited')
        user = self.request.user
        if is_favorited == "1" and not user.is_anonymous:
            queryset = queryset.filter(favourite__author=user)

        is_in_shopping_cart = self.request.query_params.get('is_in_shopping_cart')
        if is_in_shopping_cart == "1" and not user.is_anonymous:
            queryset = queryset.filter(shoppingcart__author=user)

        print(is_favorited, type(is_favorited), is_in_shopping_cart, type(is_in_shopping_cart))

        author_id = self.request.query_params.get('author')
        if author_id is not None:
            queryset = queryset.filter(author_id=author_id)

        return queryset

    @action(detail=True, methods=['get'], url_path='get-link', url_name="get_link")
    def get_link(self, request, pk=None):
        """
        GET /recipes/{id}/short-link/
        Возвращает JSON {"short-link": "<uri>"} или 404, если рецепт не найден.
        """
        recipe = get_object_or_404(Recipe, pk=pk)

        full_url = request.build_absolute_uri(
            reverse('recipes-detail', args=[recipe.pk])
        )

        shortener = pyshorteners.Shortener()
        short_url = shortener.tinyurl.short(full_url)

        return Response({"short-link": short_url}, status=status.HTTP_200_OK)


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
