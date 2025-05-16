import base64
from io import BytesIO

from django.http.response import FileResponse
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (Ingredient, Recipe,
                            Favourite, ShoppingCart,
                            RecipeIngredient, FoodgramUser,
                            Subscriber)
from .filters import IngredientFilter
from .paginators import ApiPagination
from .permissions import AuthorPermission
from .serializers import (IngredientSerializer, RecipeSerializer,
                          RecipeMinSerializer, UserAvatarSerializer,
                          UserSubSerializer)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Просмотр ингредиентов
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Класс для управления рецептами
    """
    pagination_class = ApiPagination
    serializer_class = RecipeSerializer

    def get_permissions(self):
        if self.action in ("create", "shopping_cart", "favorite",
                           "download_shopping_cart"):
            return [IsAuthenticated()]
        elif self.action in ("list", "retrieve", "get_link"):
            return [AllowAny()]
        elif self.action in ("partial_update", "destroy"):
            return [IsAuthenticated(), AuthorPermission()]
        raise MethodNotAllowed(f"Method {self.action} is not allowed")

    def get_queryset(self):
        queryset = Recipe.objects.all()

        is_favorited = self.request.query_params.get("is_favorited")
        user = self.request.user
        if is_favorited == "1" and not user.is_anonymous:
            queryset = queryset.filter(favourites__author=user)

        is_in_shopping_cart = (self.request.query_params.
                               get("is_in_shopping_cart"))
        if is_in_shopping_cart == "1" and not user.is_anonymous:
            queryset = queryset.filter(shoppingcarts__author=user)

        author_id = self.request.query_params.get("author")
        if author_id is not None:
            queryset = queryset.filter(author_id=author_id)

        return queryset

    @action(detail=True, methods=["post", "delete"], url_path="favorite")
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == "POST":
            obj, created = (Favourite.objects.
                            get_or_create(author=request.user, recipe=recipe))
            if not created:
                return Response({"detail": "Рецепт уже в избранном"},
                                status=status.HTTP_400_BAD_REQUEST)
            data = RecipeMinSerializer(recipe,
                                       context={"request": request}).data
            return Response(data, status=status.HTTP_201_CREATED)
        """
        Здесь в тестах postman ожидается статус 400 и
        в документации тоже написано 400, поэтому я не использовал
        get_object_or_404
        """
        fav = Favourite.objects.filter(author=request.user,
                                       recipe=recipe)
        if not fav:
            return Response({"detail": "Рецепта в избранном не было"},
                            status=status.HTTP_400_BAD_REQUEST)
        fav.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post", "delete"], url_path="shopping_cart")
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == "POST":
            obj, created = (ShoppingCart.objects.
                            get_or_create(author=request.user, recipe=recipe))
            if not created:
                return Response({"error": "Рецепт уже в корзине"},
                                status=status.HTTP_400_BAD_REQUEST)
            data = RecipeMinSerializer(recipe,
                                       context={"request": request}).data
            return Response(data, status=status.HTTP_201_CREATED)

        """
        Здесь ситуация такая же как в favourites
        """
        recipe_cart = (ShoppingCart.objects.
                       filter(author=request.user, recipe=recipe))
        if not recipe_cart:
            return Response({"detail": "Рецепта в списке покупок не было"},
                            status=status.HTTP_400_BAD_REQUEST)
        recipe_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], url_path="download_shopping_cart")
    def download_shopping_cart(self, request):
        user = request.user
        ingredients_dict = {}

        recipes_cart = ShoppingCart.objects.filter(author=user)

        for recipe_cart in recipes_cart:
            recipe = recipe_cart.recipe
            for ri in RecipeIngredient.objects.filter(recipe=recipe):
                name = ri.ingredient.name.capitalize()
                amount = ri.amount
                unit = ri.ingredient.measurement_unit
                if name in ingredients_dict:
                    ingredients_dict[name]["amount"] += amount
                else:
                    ingredients_dict[name] = {"amount": amount, "unit": unit}

        lines = [
            f"Список ингредиентов на {now().strftime("%Y-%m-%d")}:",
            "",
            "Ингредиенты:"
        ]

        for idx, (name, det) in enumerate(ingredients_dict.items(), start=1):
            lines.append(f"{idx}. {name}: {det["amount"]} "
                         f"{det["unit"]}")

        lines.append("")
        lines.append("Рецепты в корзине:")
        for recipe_cart in recipes_cart:
            recipe = recipe_cart.recipe
            lines.append(f"- {recipe.name} (автор:"
                         f" {recipe.author.get_full_name()})")

        file_content = "\n".join(lines)
        buffer = BytesIO()
        buffer.write(file_content.encode("utf-8"))
        buffer.seek(0)

        response = FileResponse(
            buffer,
            as_attachment=True,
            filename="shopping_list.txt",
            content_type="text/plain; charset=utf-8"
        )
        return response

    @action(["get"], detail=True, url_path="get-link")
    def get_link(self, request, pk):
        """Создание короткой ссылки через хэширование id"""
        recipe = get_object_or_404(Recipe, pk=pk)
        encoded_id = base64.urlsafe_b64encode(str(recipe.id).
                                              encode()).decode().rstrip("=")
        base_url = request.build_absolute_uri("/").rstrip("/")
        return Response({"short-link": f"{base_url}/s/{encoded_id}"},
                        status=status.HTTP_200_OK)


class UserViewSet(DjoserUserViewSet):
    """
    Класс для управления пользователем
    """

    pagination_class = ApiPagination

    @action(detail=False, methods=["put"],
            permission_classes=[IsAuthenticated], url_path="me/avatar")
    def avatar(self, request):
        serializer = UserAvatarSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @avatar.mapping.delete
    def avatar_delete(self, request):
        request.user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post", "delete"],
            permission_classes=[IsAuthenticated], url_path="subscribe")
    def subscribe(self, request, id=None):
        publisher = get_object_or_404(FoodgramUser, id=id)
        subscriber = request.user

        if request.method == "POST":
            if publisher == subscriber:
                return Response({"detail": "Нельзя подписаться на себя"},
                                status=status.HTTP_400_BAD_REQUEST)
            obj, created = (Subscriber.objects.
                            get_or_create(subscriber=subscriber,
                                          publisher=publisher))
            if not created:
                return Response({"detail": "Вы уже подписаны"},
                                status=status.HTTP_400_BAD_REQUEST)
            data = UserSubSerializer(publisher,
                                     context={"request": request}).data
            return Response(data, status=status.HTTP_201_CREATED)

        """
        Здесь опять ситуация такая же
        """
        subscribe = Subscriber.objects.filter(subscriber=subscriber,
                                              publisher=publisher)
        if not subscribe:
            return Response({"detail": "Подписки не было"},
                            status=status.HTTP_400_BAD_REQUEST)
        subscribe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"],
            permission_classes=[IsAuthenticated],
            url_path="subscriptions")
    def subscriptions(self, request):
        publisher_ids = (Subscriber.objects.filter(subscriber=request.user).
                         values_list("publisher_id", flat=True))
        qs = FoodgramUser.objects.filter(id__in=publisher_ids)
        page = self.paginate_queryset(qs)
        serializer = UserSubSerializer(page or qs, many=True,
                                       context={"request": request})
        return self.get_paginated_response(serializer.data)
