from django.contrib import admin

from .models import Ingredient


class IngredientAdmin(admin.ModelAdmin):
    model = Ingredient
    list_display = ("name", "measurement_unit")
    ordering = ("name",)
    search_fields = ("name",)


admin.site.register(Ingredient, IngredientAdmin)
