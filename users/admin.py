# users/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    # Чтобы было удобно добавлять/убирать группы и permissions стрелками
    filter_horizontal = ("groups", "user_permissions")

    ordering = ("email",)
    list_display = ("email", "is_staff", "is_superuser", "is_active")
    search_fields = ("email",)
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "avatar", "phone", "country")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "is_active", "is_staff", "is_superuser", "groups"),
        }),
    )

    # ВАЖНО: username убран в твоей модели — говорим админке не ждать его
    def get_fieldsets(self, request, obj=None):
        return super().get_fieldsets(request, obj)