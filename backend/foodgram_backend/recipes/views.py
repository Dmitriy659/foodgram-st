import io

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response
from .models import Recipe, Favourite, ShoppingCart, RecipeIngredient
from .serializers import RecipeSerializer, FavouriteSerializer, ShoppingCartSerializer
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


class BaseRecipeActionView(APIView):
    permission_classes = [IsAuthenticated]
    model = None
    serializer_class = None
    not_found_message = ""

    def post(self, request, recipe_id):
        try:
            recipe = Recipe.objects.get(pk=recipe_id)
        except Recipe.DoesNotExist:
            return Response(
                {"detail": self.not_found_message},
                status=status.HTTP_404_NOT_FOUND
            )

        if self.model.objects.filter(author=request.user, recipe=recipe).exists():
            return Response(
                status=status.HTTP_400_BAD_REQUEST
            )

        instance = self.model.objects.create(author=request.user, recipe=recipe)
        serializer = self.serializer_class(instance, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        try:
            recipe = Recipe.objects.get(pk=recipe_id)
        except Recipe.DoesNotExist:
            return Response(
                {"detail": self.not_found_message},
                status=status.HTTP_404_NOT_FOUND
            )

        instance = self.model.objects.filter(author=request.user, recipe=recipe).first()
        if not instance:
            return Response(
                status=status.HTTP_400_BAD_REQUEST
            )

        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavouritesView(BaseRecipeActionView):
    model = Favourite
    serializer_class = FavouriteSerializer
    not_found_message = "Этого рецепта нет в избранных"


class ShoppingCartView(BaseRecipeActionView):
    model = ShoppingCart
    serializer_class = ShoppingCartSerializer
    not_found_message = "Этого рецепта нет в списке покупок"


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
