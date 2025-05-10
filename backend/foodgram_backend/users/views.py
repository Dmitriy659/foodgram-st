from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models.query import Prefetch
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView

from .serializers import (PasswordChangeSerializer, FoodgramUserSerializer,
                          UserAvatarSerializer, FoodgramUserCreateSerializer, SubscriptionsSerializer)
from .pagination import CustomPagination
from .models import FoodgramUser, Subscriber

from recipes.models import Recipe

User = get_user_model()


class UserViewSet(mixins.CreateModelMixin,  # для регистрации
                  mixins.ListModelMixin,    # для списка пользователей
                  mixins.RetrieveModelMixin,  # для получения пользователя по id
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return FoodgramUserCreateSerializer  # регистрация
        return FoodgramUserSerializer


class MeView(APIView):  # текущий пользователь
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = FoodgramUserSerializer(request.user)
        return Response(serializer.data)


class UserAvatarView(APIView):
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        publisher = get_object_or_404(FoodgramUser, id=user_id)

        if request.user == publisher:
            return Response(
                {"detail": "Невозможно подписаться на самого себя."},
                status=status.HTTP_400_BAD_REQUEST
            )

            # Проверка на уже существующую подписку
        if Subscriber.objects.filter(subscriber=request.user, publisher=publisher).exists():
            return Response(
                {"detail": "Вы уже подписаны на этого пользователя."},
                status=status.HTTP_400_BAD_REQUEST
            )

        Subscriber.objects.create(subscriber=request.user, publisher=publisher)

        # Возвращаем информацию о пользователе с подпиской
        publisher_data = SubscriptionsSerializer(
            publisher,
            context={'request': request}
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
    """Получение списка подписок текущего пользователя."""
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionsSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = FoodgramUser.objects.filter(
            publishers__subscriber=self.request.user
        ).prefetch_related(
            Prefetch(
                'recipes',
                queryset=Recipe.objects.only('id', 'name', 'image', 'cooking_time')
            )
        ).distinct()

        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            for item in response.data['results']:
                item['recipes'] = item['recipes'][:int(recipes_limit)]

        return response
