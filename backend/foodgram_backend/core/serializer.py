from rest_framework.serializers import SerializerMethodField, ModelSerializer

from recipes.models import Recipe


class RecipeMinSerializer(ModelSerializer):
    """Мини-сериализатор для Recipe: id, name, image (с абсолютным URL), cooking_time"""
    image = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None