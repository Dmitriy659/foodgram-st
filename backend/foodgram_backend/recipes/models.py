from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.fields.related import ManyToManyField

from users.models import FoodgramUser
from ingredients.models import Ingredient


class Recipe(models.Model):
    author = models.ForeignKey(FoodgramUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=256, blank=False, null=False)
    text = models.TextField(blank=False, null=False)
    cooking_time = models.IntegerField(blank=False, null=False,
                                       validators=[MinValueValidator(1)])
    ingredients = ManyToManyField(
        verbose_name="Ингредиенты блюда",
        related_name="recipes",
        to=Ingredient,
        through="RecipeIngredient",
    )
    image = models.ImageField(blank=False, null=False)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.IntegerField(null=False, blank=False, validators=[MinValueValidator(1)])
