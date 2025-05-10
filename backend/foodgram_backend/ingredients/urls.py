from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet

router = DefaultRouter()
router.register(r"", IngredientViewSet, basename="ingredients")

urlpatterns = [
    path("", include(router.urls)),
]
