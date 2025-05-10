from collections import defaultdict

from .models import RecipeIngredient, Ingredient


def set_ingredients(recipe, ingredients):
    """
    Создание связи между ингредиентами и рецептом
    """
    objs = []
    ingredients_amount = defaultdict(int)

    for item in ingredients:
        ingredient = Ingredient.objects.get(pk=item.get("id"))
        amount = item.get("amount")
        ingredients_amount[ingredient] += amount

    for ingredient, amount in ingredients_amount.items():
        objs.append(
            RecipeIngredient(
                recipe=recipe, ingredient=ingredient, amount=amount
            )
        )

    RecipeIngredient.objects.bulk_create(objs)
