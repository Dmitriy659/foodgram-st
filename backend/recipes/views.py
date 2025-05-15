import base64

from django.http.response import HttpResponseRedirect, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django.urls.base import reverse

from .models import Recipe


def redirect_shorturl(request, short_link):
    """Перенаправление с короткой ссылки"""
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    try:
        padded = short_link + "=" * (-len(short_link) % 4)
        decoded_id = int(base64.urlsafe_b64decode(padded).decode())
        recipe = get_object_or_404(Recipe, pk=decoded_id)
        return HttpResponseRedirect(request.build_absolute_uri(
            reverse("api:recipes-detail", args=[recipe.pk])
        ))
    except Exception as e:
        return HttpResponseRedirect('/')
