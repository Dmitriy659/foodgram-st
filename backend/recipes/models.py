from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.fields.related import ManyToManyField
from ingredients.models import Ingredient
from users.models import FoodgramUser


class Recipe(models.Model):
    """
    Модель рецепта
    """
    author = models.ForeignKey(FoodgramUser,
                               on_delete=models.CASCADE,
                               related_name="recipes")
    name = models.CharField(max_length=256, blank=False, null=False)
    text = models.TextField(blank=False, null=False)
    cooking_time = models.IntegerField(blank=False, null=False,
                                       validators=[MinValueValidator(1)])
    create_date = models.DateTimeField(auto_now_add=True)
    ingredients = ManyToManyField(
        verbose_name="Ингредиенты блюда",
        related_name="recipes",
        to=Ingredient,
        through="RecipeIngredient",
    )
    image = models.ImageField(blank=False, null=False, upload_to="recipes/")

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ("author", "name")
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"


class RecipeIngredient(models.Model):
    """
    Связь рецепт - ингредиенты
    """
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name="recipe_ingredients")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.IntegerField(null=False,
                                 blank=False,
                                 validators=[MinValueValidator(1)])

    class Meta:
        unique_together = ("recipe", "ingredient")


class Favourite(models.Model):
    """
    Рецепты в избранном
    """
    author = models.ForeignKey(FoodgramUser, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.author} - {str(self.recipe)}"

    class Meta:
        unique_together = ("author", "recipe")
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"


class ShoppingCart(models.Model):
    """
    Рецепты в списке покупок
    """
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    author = models.ForeignKey(FoodgramUser, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.author} - {self.recipe}"

    class Meta:
        unique_together = ("author", "recipe")
        verbose_name = "Список покупок"
        verbose_name_plural = "Список покупок"
