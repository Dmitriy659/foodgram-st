from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import RecipeViewSet, UserViewSet, IngredientViewSet

app_name = "api"

router = DefaultRouter()
router.register(r"recipes", RecipeViewSet, basename="recipes")
router.register(r"users", UserViewSet, basename="users")
router.register(r"ingredients", IngredientViewSet, basename="ingredients")

urlpatterns = [
    path("api/auth/", include("djoser.urls.authtoken")),
    path("api/", include(router.urls)),
]
