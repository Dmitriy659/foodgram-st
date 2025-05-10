from recipes.models import Recipe
from rest_framework.serializers import SerializerMethodField, ModelSerializer


class RecipeMinSerializer(ModelSerializer):
    """
    Сериализатор с уменьшенным кол-вом полей
    """
    image = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None
