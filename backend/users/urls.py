from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet, UserAvatarView,
    SubscriptionsListView, SubscriptionsView
)

router = DefaultRouter()
router.register(r"", UserViewSet, basename="users")

urlpatterns = [
    path("me/avatar/", UserAvatarView.as_view(),
         name="avatar"),  # PUT/DELETE
    path("subscriptions/", SubscriptionsListView.as_view(),
         name="subscriptions"),
    path("<int:user_id>/subscribe/",
         SubscriptionsView.as_view(),
         name="user-subscribe"),
    path('', include(router.urls)),  # POST/GET
]
