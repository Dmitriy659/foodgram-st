from django.shortcuts import get_object_or_404, redirect

from .models import Recipe


def redirect_shorturl(request, recipe_id):
    """Перенаправление с короткой ссылки"""
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    return redirect(f'/recipes/{recipe.pk}')
