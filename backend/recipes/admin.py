from django.contrib import admin
from django.contrib.admin.filters import SimpleListFilter
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe

from .models import (Recipe,
                     Favourite, ShoppingCart,
                     Ingredient, Subscriber, FoodgramUser)


class CookingTimeFilter(SimpleListFilter):
    """
    Фильтр делящий рцепты на быстрые, средние и долгие
    """
    title = "время готовки"
    parameter_name = "cooking_time_bin"
    n = None
    m = None

    def lookups(self, request, model_admin):
        recipes = Recipe.objects.all()
        times = list(recipes.values_list("cooking_time", flat=True))

        if len(set(times)) < 3:
            return []

        times.sort()
        self.n = times[len(times) // 3]
        self.m = times[2 * len(times) // 3]

        def count_in_range(lower, upper=None):
            q = recipes
            if upper is None:
                q = q.filter(cooking_time__gte=lower)
            else:
                q = q.filter(cooking_time__gte=lower, cooking_time__lt=upper)
            return q.count()

        return [
            ("fast", f"быстро (< {self.n} мин) ({count_in_range(0, self.n)})"),
            ("medium", f"средне (от {self.n} до {self.m} мин)"
                       f" ({count_in_range(self.n, self.m)})"),
            ("slow", f"долго (≥ {self.m} мин) ({count_in_range(self.m)})"),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        n = getattr(self, 'n')
        m = getattr(self, 'm')

        if value == "fast":
            return queryset.filter(cooking_time__lt=n)
        elif value == "medium":
            return queryset.filter(cooking_time__gte=n, cooking_time__lt=m)
        elif value == "slow":
            return queryset.filter(cooking_time__gte=m)
        return queryset


class HasRelationFilter(SimpleListFilter):
    """Базовый фильтр: наличие связанного объекта"""

    LOOKUP_CHOICES = [
        ("yes", "Есть"),
        ("no", "Нет"),
    ]

    related_field = None  # задаётся в наследниках

    def lookups(self, request, model_admin):
        return self.LOOKUP_CHOICES

    def queryset(self, request, queryset):
        value = self.value()
        if value == "yes":
            return queryset.filter(
                **{f"{self.related_field}__isnull": False}).distinct()
        elif value == "no":
            return queryset.filter(
                **{f"{self.related_field}__isnull": True}).distinct()
        return queryset


class HasRecipesFilter(HasRelationFilter):
    """Фильтр есть ли рецепты"""

    title = "Есть рецепты"
    parameter_name = "has_recipes"
    related_field = "recipes"


class HasSubscriptionsFilter(HasRelationFilter):
    """Фильтр есть ли подписки"""

    title = "Есть подписки"
    parameter_name = "has_subscriptions"
    related_field = "publishers"


class HasSubscribersFilter(HasRelationFilter):
    """Фильтр есть ли подписчики"""

    title = "Есть подписчики"
    parameter_name = "has_subscribers"
    related_field = "subscribers"


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "cooking_time", "author",
                    "favorites_count", "formatted_ingredients", "image")
    search_fields = ("name", "author__username")
    list_filter = ("author",
                   CookingTimeFilter)

    @admin.display(description="В избранном")
    def favorites_count(self, recipe):
        return recipe.favourites.count()

    @admin.display(description="Продукты")
    def formatted_ingredients(self, recipe):
        return mark_safe("<br>".join([
            f"{ri.ingredient.name} - {ri.amount}"
            f" {ri.ingredient.measurement_unit}"
            for ri in recipe.recipe_ingredients.select_related(
                "ingredient").all()
        ]))

    @admin.display(description="Картинка")
    def image(self, recipe):
        return mark_safe(f'<img src="{recipe.image.url}" width="100" />')


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ("author", "recipe")
    search_fields = ("author__username", "recipe__name")


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ("author", "recipe")
    search_fields = ("author__username", "recipe__name")


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    model = Ingredient
    list_display = ("name", "measurement_unit", "recipes_count")
    ordering = ("name",)
    search_fields = ("name", "measurement_unit")
    list_filter = ("measurement_unit",)

    @admin.display(description="Число рецептов")
    def recipes_count(self, obj):
        return obj.recipes.count()


@admin.register(FoodgramUser)
class FoodgramUserAdmin(UserAdmin):
    model = FoodgramUser
    list_display = (
        "id",
        "username",
        "full_name",
        "email",
        "avatar_tag",
        "recipes_count",
        "subscriptions_count",
        "subscribers_count",
        "is_superuser"
    )
    search_fields = ("email", "username")
    ordering = ("email",)

    list_filter = (
        "is_superuser",
        HasRecipesFilter,
        HasSubscriptionsFilter,
        HasSubscribersFilter,
    )

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("username",
                                      "first_name", "last_name")}),
        ("Permissions", {
            "fields": ("is_active", "is_staff",
                       "is_superuser", "groups", "user_permissions"),
        }),
        ("Important Dates", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "username", "first_name",
                       "last_name", "password1", "password2",
                       "is_staff", "is_superuser", "is_active")}
         ),
    )

    @admin.display(description="ФИО")
    def full_name(self, user):
        return f"{user.first_name} {user.last_name}"

    @admin.display(description="Аватар")
    def avatar_tag(self, user):
        if user.avatar:
            return mark_safe(f'<img src="{user.avatar.url}"'
                             f' width="50" height="50"" />')
        return "-"

    @admin.display(description="Рецепты")
    def recipes_count(self, user):
        return Recipe.objects.filter(author=user).count()

    @admin.display(description="Подписчики")
    def subscriptions_count(self, user):
        return Subscriber.objects.filter(subscriber=user).count()

    @admin.display(description="Подписки")
    def subscribers_count(self, user):
        return Subscriber.objects.filter(publisher=user).count()


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ("subscriber", "publisher")
    search_fields = ("subscriber__email", "publisher__email")
    list_filter = ("subscriber", "publisher")
