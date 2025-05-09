from rest_framework import serializers
from .models import FoodgramUser
from .fields import Base64ImageField


class FoodgramUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = FoodgramUser
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name',
            'password', 'is_subscribed', 'avatar',
        )

    def get_is_subscribed(self, obj):
        return False  # Заглушка — всегда возвращаем False


class FoodgramUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = FoodgramUser
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name', "password"
        )

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = FoodgramUser(**validated_data)
        user.set_password(password)
        user.save()
        return user


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class UserAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = FoodgramUser
        fields = ("avatar",)
