from django.core.exceptions import ValidationError
from django.db.transaction import atomic
from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import (SerializerMethodField, ModelSerializer,
                                        IntegerField, ReadOnlyField,
                                        PrimaryKeyRelatedField)

from recipes.models import (Recipe, Ingredient, Favourite,
                            ShoppingCart, RecipeIngredient,
                            FoodgramUser, Subscriber)


class RecipeMinSerializer(ModelSerializer):
    """
    Сериализатор с уменьшенным кол-вом полей
    """

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = ("__all__",)


class IngredientSerializer(ModelSerializer):
    """
    Сериализатор для ингредиентов
    """

    class Meta:
        model = Ingredient
        fields = "__all__"


class RecipeIngredientSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(source="ingredient",
                                queryset=Ingredient.objects.all())
    name = ReadOnlyField(source="ingredient.name")
    measurement_unit = ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class FoodgramUserSerializer(DjoserUserSerializer):
    """
    Сериализатор для получения данных о пользователях
    """
    is_subscribed = SerializerMethodField(read_only=True)
    avatar = Base64ImageField(required=False)

    class Meta:
        model = FoodgramUser
        fields = (
            "id", "email", "username",
            "first_name", "last_name",
            "is_subscribed", "avatar",
        )
        read_only_fields = ("is_subscribed", "avatar")

    def get_is_subscribed(self, viewed_user):
        request = self.context.get("request")
        return (request
                and hasattr(request, "user")
                and request.user.is_authenticated
                and Subscriber.objects.
                filter(publisher=viewed_user,
                       subscriber=request.user).exists())


class RecipeSerializer(ModelSerializer):
    """
    Сериализатор для рецептов
    """

    author = FoodgramUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(source="recipe_ingredients",
                                             many=True, read_only=True)
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id", "author", "ingredients", "is_favorited",
            "is_in_shopping_cart",
            "name", "image", "text", "cooking_time",
        )
        read_only_fields = (
            "is_favorite", "is_shopping_cart",
        )

    def get_is_favorited(self, recipe: Recipe) -> bool:
        """
        Проверка, находится ли рецепт в избранном
        """
        user = self.context["request"].user
        return (user.is_authenticated
                and Favourite.objects.filter(author=user,
                                             recipe=recipe).exists())

    def get_is_in_shopping_cart(self, recipe: Recipe) -> bool:
        """
        Проверка, находится ли рецепт в списке  покупок
        """
        user = self.context["request"].user
        return (user.is_authenticated
                and ShoppingCart.objects.filter(author=user,
                                                recipe=recipe).exists())

    def validate(self, data):
        """
        Проверка вводных данных при создании/редактировании рецепта
        """
        ingredients = self.initial_data.get("ingredients")
        if not ingredients:
            raise ValidationError("Ингредиентов нет")
        if "image" in data and not data["image"]:
            raise ValidationError("Нет изображения")
        if len(ingredients) != len(set(item["id"] for item in ingredients)):
            raise ValidationError("Ингредиенты должны быть уникальными")
        if not all((int(item["amount"]) > 0 for item in ingredients)):
            raise ValidationError("Кол-во должно быть больше 0")
        if not all((Ingredient.objects.filter(pk=item["id"]).exists() for item in ingredients)):
            raise ValidationError("Такого рецепта не существует")

        data["ingredients"] = ingredients
        return data

    @atomic
    def create(self, validated_data: dict) -> Recipe:
        """Создаёт рецепт"""
        ingredients = validated_data.pop("ingredients")
        validated_data["author"] = self.context["request"].user
        recipe = super().create(validated_data)
        self.set_ingredients(recipe, ingredients)

        return recipe

    @atomic
    def update(self, recipe: Recipe, validated_data: dict) -> Recipe:
        """Обновляет рецепт"""
        ingredients = validated_data.pop("ingredients", None)
        recipe = super().update(recipe, validated_data)

        recipe.ingredients.clear()
        self.set_ingredients(recipe, ingredients)

        return recipe

    def set_ingredients(self, recipe, ingredients_data):
        """
        Создаёт связи между рецептом и ингредиентами.
        """
        recipe_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=Ingredient.objects.get(pk=item["id"]),
                amount=item["amount"],
            )
            for item in ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)


class UserAvatarSerializer(ModelSerializer):
    """
    Сериализатор для управления аватарками
    """
    avatar = Base64ImageField(required=True)

    class Meta:
        model = FoodgramUser
        fields = ("avatar",)


class UserSubSerializer(FoodgramUserSerializer):
    """
    Сериализатор для пользоватлея с подписками
    """
    recipes = SerializerMethodField()
    recipes_count = IntegerField(source="recipes.count", read_only=True)

    class Meta:
        model = FoodgramUser
        fields = (
            "id", "username", "email", "first_name",
            "last_name", "is_subscribed", "recipes", "recipes_count", "avatar"
        )

    def get_recipes(self, obj):
        request = self.context.get("request")
        qs = obj.recipes.all()
        limit = request.query_params.get("recipes_limit") if request else None
        if limit:
            try:
                qs = qs[:int(limit)]
            except ValueError:
                pass
        return RecipeMinSerializer(qs, many=True,
                                   context={"request": request}).data
