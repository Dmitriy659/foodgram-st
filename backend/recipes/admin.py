from django.contrib import admin
from django.contrib.admin.filters import SimpleListFilter
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe

from .models import (Recipe, RecipeIngredient,
                     Favourite, ShoppingCart,
                     Ingredient, Subscriber, FoodgramUser)


class CookingTimeFilter(SimpleListFilter):
    """
    Фильтр делящий рцепты на быстрые, средние и долгие
    """
    title = "время готовки"
    parameter_name = "cooking_time_bin"

    def lookups(self, request, model_admin):
        recipes = Recipe.objects.all()
        times = list(recipes.values_list("cooking_time", flat=True))
        if not times:
            return []

        times.sort()
        n = times[len(times) // 3]
        m = times[2 * len(times) // 3]

        def count_in_range(lower, upper=None):
            q = recipes
            if upper is None:
                q = q.filter(cooking_time__gte=lower)
            else:
                q = q.filter(cooking_time__gte=lower, cooking_time__lt=upper)
            return q.count()

        return [
            ("fast", f"быстро (< {n} мин) ({count_in_range(0, n)})"),
            ("medium", f"средне (от {n} до {m} мин) ({count_in_range(n, m)})"),
            ("slow", f"долго (≥ {m} мин) ({count_in_range(m)})"),
        ]

    def queryset(self, request, queryset):
        times = list(queryset.values_list("cooking_time", flat=True))
        if not times:
            return queryset

        times.sort()
        n = times[len(times) // 3]
        m = times[2 * len(times) // 3]

        value = self.value()
        if value == "fast":
            return queryset.filter(cooking_time__lt=n)
        elif value == "medium":
            return queryset.filter(cooking_time__gte=n, cooking_time__lt=m)
        elif value == "slow":
            return queryset.filter(cooking_time__gte=m)
        return queryset


class HasRecipesFilter(SimpleListFilter):
    """
    Фильтр по пользовтелям, есть ли рецепты
    """
    title = "Есть рецепты"
    parameter_name = "has_recipes"

    def lookups(self, request, model_admin):
        return [
            ("yes", "Есть"),
            ("no", "Нет"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(recipes__isnull=False).distinct()
        if self.value() == "no":
            return queryset.filter(recipes__isnull=True).distinct()
        return queryset


class HasSubscriptionsFilter(SimpleListFilter):
    """
    Фильтр по пользовтелям, есть ли подписки
    """
    title = "Есть подписки"
    parameter_name = "has_subscriptions"

    def lookups(self, request, model_admin):
        return [
            ("yes", "Есть"),
            ("no", "Нет"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(publishers__isnull=False).distinct()
        if self.value() == "no":
            return queryset.filter(publishers__isnull=True).distinct()
        return queryset


class HasSubscribersFilter(SimpleListFilter):
    """
    Фильтр по пользовтелям, есть ли подписчики
    """
    title = "Есть подписчики"
    parameter_name = "has_subscribers"

    def lookups(self, request, model_admin):
        return [
            ("yes", "Есть"),
            ("no", "Нет"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(subscribers__isnull=False).distinct()
        if self.value() == "no":
            return queryset.filter(subscribers__isnull=True).distinct()
        return queryset


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "cooking_time", "author",
                    "favorites_count", "ingredients", "image")
    search_fields = ("name", "author__username")
    list_filter = ("author",
                   CookingTimeFilter)
    inlines = [RecipeIngredientInline]

    @admin.display(description="В избранном")
    def favorites_count(self, recipe):
        return recipe.favourites.count()

    @admin.display(description="Продукты")
    def ingredients(self, recipe):
        ingredients = recipe.ingredients.all()
        return mark_safe("<br>".join(
            f"{ing.name} ({ing.measurement_unit})" for ing in ingredients
        ))

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

    @admin.display(description="Число рецептов")
    def recipes_count(self, user):
        return Recipe.objects.filter(author=user).count()

    @admin.display(description="Число подписок")
    def subscriptions_count(self, user):
        return Subscriber.objects.filter(subscriber=user).count()

    @admin.display(description="Число подписчиков")
    def subscribers_count(self, user):
        return Subscriber.objects.filter(publisher=user).count()

    @admin.display(boolean=True, description="Есть рецепты")
    def has_recipes(self, user):
        return Recipe.objects.filter(author=user).exists()

    @admin.display(boolean=True, description="Есть подписки")
    def has_subscriptions(self, user):
        return Subscriber.objects.filter(subscriber=user).exists()

    @admin.display(boolean=True, description="Есть подписчики")
    def has_subscribers(self, user):
        return Subscriber.objects.filter(publisher=user).exists()


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ("subscriber", "publisher")
    search_fields = ("subscriber__email", "publisher__email")
    list_filter = ("subscriber", "publisher")
