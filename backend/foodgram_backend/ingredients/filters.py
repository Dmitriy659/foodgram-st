import django_filters

from .models import Ingredient


class IngredientFilter(django_filters.FilterSet):
    """
    Фильтр поиска ингредиентов
    """
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Ingredient
        fields = ['name']
