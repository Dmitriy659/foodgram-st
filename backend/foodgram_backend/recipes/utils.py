from .models import RecipeIngredient

from ingredients.models import Ingredient

def set_ingredients(recipe, ingredients):
    objs = []

    for item in ingredients:
        ingredient = Ingredient.objects.get(pk=item.get('id'))
        amount = item.get('amount')
        objs.append(
            RecipeIngredient(
                recipe=recipe, ingredient=ingredient, amount=amount
            )
        )

    RecipeIngredient.objects.bulk_create(objs)