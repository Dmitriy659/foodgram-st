from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from django.db import transaction

from .models import Recipe, RecipeIngredient
from ingredients.models import Ingredient
from users.serializers import FoodgramUserSerializer
from ingredients.serializers import IngredientSerializer


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField(),
        ),
        write_only=True
    )
    image = Base64ImageField(write_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients', 'image', 'name', 'text', 'cooking_time')

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        user = self.context['request'].user
        validated_data['author'] = user

        with transaction.atomic():
            recipe = Recipe.objects.create(**validated_data)
            for item in ingredients_data:
                ing = Ingredient.objects.filter(id=item['id']).first()
                if not ing:
                    raise serializers.ValidationError(
                        f"Ingredient с id={item['id']} не найден."
                    )
                RecipeIngredient.objects.create(
                    recipe=recipe,
                    ingredient=ing,
                    amount=item['amount']
                )
        return recipe
