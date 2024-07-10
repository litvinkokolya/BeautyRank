from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.utils.translation import gettext_lazy as _

from .forms import UserCreateForm
from .models import *


@admin.register(User)
class CustomUserAdmin(ModelAdmin):
    add_form = UserCreateForm
    list_display = ("id", "last_name", "phone_number", "is_staff", "date_joined")
    list_display_links = ("last_name", "phone_number")
    search_fields = ("last_name", "phone_number")
    ordering = ["last_name"]
    fieldsets = (
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone_number",
                    "image",
                    "optimized_image",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
