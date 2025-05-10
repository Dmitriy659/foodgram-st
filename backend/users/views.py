from core.pagination import CustomPagination
from core.permissions import IsAuthenticatedBanned
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from recipes.models import Recipe
from rest_framework import viewsets, mixins, status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import FoodgramUser, Subscriber
from .serializers import (PasswordChangeSerializer, FoodgramUserSerializer,
                          UserAvatarSerializer, FoodgramUserCreateSerializer, SubscriptionsSerializer)

User = get_user_model()


class UserViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    """
    Получение списка юзеров с указанием, на кого подписан текущий,
    создание юзера и получение данных одного пользвоателя
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == "create":
            return FoodgramUserCreateSerializer
        return FoodgramUserSerializer


class MeView(APIView):
    """
    Получение данных о текущем пользователе
    """
    permission_classes = [IsAuthenticatedBanned]

    def get(self, request):
        serializer = FoodgramUserSerializer(request.user)
        return Response(serializer.data)


class UserAvatarView(APIView):
    """
    Добавление или удаление аватарки у текущего юзера
    """
    permission_classes = [IsAuthenticatedBanned]

    def put(self, request):
        serializer = UserAvatarSerializer(
            request.user, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request):
        user = request.user
        user.avatar.delete(save=True)
        return Response(status=204)


class SetPasswordView(APIView):
    """
    Изменение пароля у текущего юзера
    """
    permission_classes = [IsAuthenticatedBanned]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user

        if not user.check_password(serializer.data["current_password"]):
            return Response({"current_password": "Wrong password"}, status=400)

        try:
            validate_password(serializer.data["new_password"], user)
        except ValidationError as e:
            return Response({"new_password": e.message}, status=400)

        user.set_password(serializer.data["new_password"])
        user.save()
        return Response(status=204)


class SubscriptionsView(APIView):
    """
    Текущий юзер создаёт или удаляет подписку на другого
    """
    permission_classes = [IsAuthenticatedBanned]

    def post(self, request, user_id):
        publisher = get_object_or_404(FoodgramUser, id=user_id)

        if (request.user == publisher or
                Subscriber.objects.filter(subscriber=request.user, publisher=publisher).exists()):
            return Response(
                status=status.HTTP_400_BAD_REQUEST
            )

        Subscriber.objects.create(subscriber=request.user, publisher=publisher)

        publisher_data = SubscriptionsSerializer(
            publisher,
            context={"request": request}
        ).data

        return Response(publisher_data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        publisher = get_object_or_404(FoodgramUser, id=user_id)
        subscriber = request.user
        subscription = Subscriber.objects.filter(subscriber=subscriber, publisher=publisher)
        if not subscription:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionsListView(ListAPIView):
    """
    Получение списка юзеров, на которых подписан текущий
    """
    serializer_class = SubscriptionsSerializer
    permission_classes = [IsAuthenticatedBanned]
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        publisher_ids = Subscriber.objects.filter(
            subscriber=user
        ).values_list("publisher_id", flat=True)
        return FoodgramUser.objects.filter(id__in=publisher_ids)
