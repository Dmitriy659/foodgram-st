from django.urls import path
from .views import redirect_shorturl

app_name = "recipes"

urlpatterns = [
    path("<int:recipe_id>/", redirect_shorturl, name="short-link-redirect"),
]
