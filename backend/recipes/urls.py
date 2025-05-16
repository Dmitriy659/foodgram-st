from django.urls import path
from .views import redirect_shorturl

app_name = "recipes"

urlpatterns = [
    path("<str:short_link>/", redirect_shorturl, name="short-link-redirect"),
]
