from core.serializers import RecipeMinSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from .models import FoodgramUser, Subscriber


class FoodgramUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для получения данных о пользователях
    """
    password = serializers.CharField(write_only=True, required=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = FoodgramUser
        fields = (
            "id", "email", "username",
            "first_name", "last_name",
            "password", "is_subscribed", "avatar",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')

        if request and hasattr(request, 'user'):
            user = request.user
            if user.is_authenticated:
                return Subscriber.objects.filter(publisher=obj,
                                                 subscriber=user).exists()

        return False


class FoodgramUserCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания юзера
    """
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = FoodgramUser
        fields = (
            "id", "email", "username",
            "first_name", "last_name", "password"
        )

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = FoodgramUser(**validated_data)
        user.set_password(password)
        user.save()
        return user


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class UserAvatarSerializer(serializers.ModelSerializer):
    """
    Сериализатор для управления аватарками
    """
    avatar = Base64ImageField(required=True)

    class Meta:
        model = FoodgramUser
        fields = ("avatar",)


class SubscriptionsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для управление подпсиками
    """
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.ImageField(read_only=True)

    class Meta:
        model = FoodgramUser
        fields = (
            "id", "username", "email", "first_name",
            "last_name", "is_subscribed", "recipes", "recipes_count", "avatar"
        )

    def get_is_subscribed(self, obj):
        return True

    def get_recipes(self, obj):
        request = self.context.get("request")
        qs = obj.recipes.all()
        limit = request.query_params.get("recipes_limit") if request else None
        if limit:
            try:
                qs = qs[:int(limit)]
            except ValueError:
                pass
        return RecipeMinSerializer(qs, many=True,
                                   context={"request": request}).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
