from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet, FavouritesView

router = DefaultRouter()
router.register(r"", RecipeViewSet, basename="recipes")

urlpatterns = [
    path("<int:recipe_id>/favorite/", FavouritesView.as_view(), name="favourite"),
    path('', include(router.urls)),
]
