from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, MeView,
    UserAvatarView, SetPasswordView,
)

router = DefaultRouter()
router.register(r"", UserViewSet, basename="users")

urlpatterns = [
    path('me/', MeView.as_view(), name='user-me'),           # GET /api/users/me/
    path('me/avatar/', UserAvatarView.as_view(), name='avatar'),  # PUT/DELETE
    path('set_password/', SetPasswordView.as_view(), name='set-password'), # POST
    path('', include(router.urls)),  # POST/GET
]
