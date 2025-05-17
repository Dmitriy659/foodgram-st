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
        read_only_fields = fields


class IngredientSerializer(ModelSerializer):
    """
    Сериализатор для ингредиентов
    """

    class Meta:
        model = Ingredient
        fields = "__all__"


class RecipeIngredientCreateSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), required=True
    )
    amount = IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ("id", "amount")


class RecipeIngredientReadSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(source="ingredient", read_only=True)
    name = ReadOnlyField(source="ingredient.name")
    measurement_unit = ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")
        read_only_fields = fields


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
        read_only_fields = fields

    def get_is_subscribed(self, viewed_user):
        request = self.context.get("request")
        return (request
                and request.user.is_authenticated
                and Subscriber.objects.
                filter(publisher=viewed_user,
                       subscriber=request.user).exists())


class RecipeSerializer(ModelSerializer):
    """
    Сериализатор для рецептов
    """

    author = FoodgramUserSerializer(read_only=True)
    ingredients = RecipeIngredientCreateSerializer(
        write_only=True, many=True
    )
    ingredients_data = RecipeIngredientReadSerializer(
        source="recipe_ingredients", many=True, read_only=True
    )
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id", "author", "ingredients", "ingredients_data",
            "is_favorited", "is_in_shopping_cart",
            "name", "image", "text", "cooking_time",
        )
        read_only_fields = (
            "is_favorite", "is_shopping_cart",
        )

    def to_representation(self, instance):
        res = super().to_representation(instance)
        res["ingredients"] = res.pop("ingredients_data")
        return res

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
        if not data["image"]:
            raise ValidationError("Нет изображения")
        if not ingredients:
            raise ValidationError("Нет ингредиентов")
        if len(ingredients) != len(set(item["id"] for item in ingredients)):
            raise ValidationError("Ингредиенты должны быть уникальными")

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

        ingredients = validated_data.pop("ingredients")
        recipe.ingredients.clear()
        self.set_ingredients(recipe, ingredients)

        return super().update(recipe, validated_data)

    def set_ingredients(self, recipe, ingredients_data):
        """
        Создаёт связи между рецептом и ингредиентами.
        """
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=item["id"],
                amount=item["amount"],
            )
            for item in ingredients_data
        ])


class UserAvatarSerializer(ModelSerializer):
    """
    Сериализатор для управления аватарками
    """
    avatar = Base64ImageField()

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
