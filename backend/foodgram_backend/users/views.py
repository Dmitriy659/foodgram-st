from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import UpdateAPIView, DestroyAPIView
from django.contrib.auth import get_user_model

from .serializers import PasswordChangeSerializer, FoodgramUserSerializer, UserAvatarSerializer

User = get_user_model()


class UserViewSet(viewsets.ReadOnlyModelViewSet):  # все пользователи или один
    queryset = User.objects.all()
    serializer_class = FoodgramUserSerializer


class RegisterView(generics.CreateAPIView):  # регистраци
    queryset = User.objects.all()
    serializer_class = FoodgramUserSerializer
    permission_classes = [AllowAny]


class MeView(APIView):  # текущий пользователь
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = FoodgramUserSerializer(request.user)
        return Response(serializer.data)


class AvatarUpdateView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserAvatarSerializer

    def get_object(self):
        return self.request.user

class AvatarDeleteView(DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserAvatarSerializer

    def get_object(self):
        return self.request.user


class SetPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        pass
        # TODO: реализовать смену пароля
