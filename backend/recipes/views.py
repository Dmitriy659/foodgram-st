from django.http.response import Http404
from django.shortcuts import redirect

from .models import Recipe


def redirect_shorturl(request, recipe_id):
    """Перенаправление с короткой ссылки"""
    if not Recipe.objects.filter(pk=recipe_id).exists():
        raise Http404(f"Рецепт {recipe_id} не найден")

    return redirect(f'/recipes/{recipe_id}')
