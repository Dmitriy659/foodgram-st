from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import FoodgramUser


@admin.register(FoodgramUser)
class FoodgramUserAdmin(UserAdmin):
    model = FoodgramUser
    list_display = ("email", "first_name",
                    "last_name", "username", "is_superuser")
    search_fields = ("email", "username")
    ordering = ("email",)

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
