from django.contrib import admin
from .models import Recipe, RecipeIngredient, Favourite, ShoppingCart


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "author", "favorites_count")
    search_fields = ("name", "author__username")
    inlines = [RecipeIngredientInline]

    def favorites_count(self, obj):
        return obj.favourite_set.count()
    favorites_count.short_description = "В избранном"


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ("author", "recipe")
    search_fields = ("author__username", "recipe__name")


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ("author", "recipe")
    search_fields = ("author__username", "recipe__name")
