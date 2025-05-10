from django.core.exceptions import ValidationError
from django.db.transaction import atomic
from drf_extra_fields.fields import Base64ImageField
from ingredients.models import Ingredient
from ingredients.serializers import IngredientSerializer
from rest_framework.serializers import SerializerMethodField, ModelSerializer, CharField, IntegerField
from users.serializers import FoodgramUserSerializer

from .models import Recipe, RecipeIngredient, Favourite, ShoppingCart
from .utils import set_ingredients


class RecipeSerializer(ModelSerializer):
    """Сериализатор для рецептов."""

    author = FoodgramUserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id", "author", "ingredients", "is_favorited", "is_in_shopping_cart",
            "name", "image", "text", "cooking_time",
        )
        read_only_fields = (
            "is_favorite", "is_shopping_cart",
        )

    def get_ingredients(self, recipe: Recipe):
        """Получает список ингридиентов для рецепта."""
        ingredients = RecipeIngredient.objects.filter(recipe=recipe).select_related("ingredient")
        return [
            {
                "id": item.ingredient.id,
                "name": item.ingredient.name,
                "measurement_unit": item.ingredient.measurement_unit,
                "amount": item.amount,
            }
            for item in ingredients
        ]

    def get_is_favorited(self, recipe: Recipe) -> bool:
        """Проверка - находится ли рецепт в избранном."""
        return False

    def get_is_in_shopping_cart(self, recipe: Recipe) -> bool:
        """Проверка - находится ли рецепт в списке  покупок."""
        return False

    def validate(self, data):
        """Проверка вводных данных при создании/редактировании рецепта."""
        ingredients = self.initial_data.get("ingredients")

        if not ingredients:
            raise ValidationError("Ингредиентов нет")

        ing_ids = [ing["id"] for ing in ingredients]
        cnt = Ingredient.objects.filter(id__in=ing_ids).count()
        if cnt < len(ing_ids):
            raise ValidationError("Некоторые ингредиенты не существуют")
        if not all(map(lambda x: x > 0, [ing["amount"] for ing in ingredients])):
            raise ValidationError("Кол-во ингридиентов меньше 1")
        if "image" in data and not data["image"]:
            raise ValidationError("Нет изображения")

        data.update(
            {
                "ingredients": ingredients,
                "author": self.context.get("request").user,
            }
        )
        return data

    @atomic
    def create(self, validated_data: dict) -> Recipe:
        """Создаёт рецепт."""
        ingredients: dict[int, tuple] = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data)
        set_ingredients(recipe, ingredients)
        return recipe

    @atomic
    def update(self, recipe: Recipe, validated_data: dict):
        """Обновляет рецепт."""
        ingredients = validated_data.pop("ingredients")

        for key, value in validated_data.items():
            if hasattr(recipe, key):
                setattr(recipe, key, value)

        if ingredients:
            recipe.ingredients.clear()
            set_ingredients(recipe, ingredients)

        recipe.save()
        return recipe


class ShoppingFavouriteSerializer(ModelSerializer):
    name = CharField(source="recipe.name", read_only=True)
    image = SerializerMethodField()
    cooking_time = IntegerField(source="recipe.cooking_time", read_only=True)

    def get_image(self, obj):
        request = self.context.get("request")
        image_field = obj.recipe.image
        if image_field:
            return request.build_absolute_uri(image_field.url)
        return None


class FavouriteSerializer(ShoppingFavouriteSerializer):
    class Meta:
        model = Favourite
        fields = ("id", "name", "image", "cooking_time")


class ShoppingCartSerializer(ShoppingFavouriteSerializer):
    class Meta:
        model = ShoppingCart
        fields = ("id", "name", "image", "cooking_time")

