from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import PasswordChangeSerializer, FoodgramUserSerializer, UserAvatarSerializer, FoodgramUserCreateSerializer
from .pagination import CustomUserPagination

User = get_user_model()


class UserViewSet(mixins.CreateModelMixin,  # для регистрации
                  mixins.ListModelMixin,    # для списка пользователей
                  mixins.RetrieveModelMixin,  # для получения пользователя по id
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    pagination_class = CustomUserPagination

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
