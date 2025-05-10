from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (RecipeViewSet, FavouritesView,
                    ShoppingCartView, DownloadShoppingCart)

router = DefaultRouter()
router.register(r"", RecipeViewSet, basename="recipes")

urlpatterns = [
    path("<int:recipe_id>/shopping_cart/", ShoppingCartView.as_view(),
         name="shopping_cart"),
    path("download_shopping_cart/", DownloadShoppingCart.as_view(),
         name="download_shopping_cart"),
    path("<int:recipe_id>/favorite/", FavouritesView.as_view(),
         name="favourite"),
    path("", include(router.urls)),
]
