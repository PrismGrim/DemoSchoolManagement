from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


class UserModelAdmin(BaseUserAdmin):
    list_display = ["id", "email", "first_name", "last_name", "is_admin"]
    list_filter = ["is_admin"]
    fieldsets = [
        ('User Credential', {"fields": ["email", "password"]}),
        ("Personal info", {"fields": ["first_name", "last_name"]}),
        ("Permissions", {"fields": ["is_admin"]}),
    ]
    
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "first_name", "last_name", "password1", "password2"],
            },
        ),
    ]
    search_fields = ["email"]
    ordering = ["email", "id"]
    filter_horizontal = []

admin.site.register(User, UserModelAdmin)
admin.site.register(Level)
admin.site.register(Role)
admin.site.register(ActivityLog)
admin.site.register(PricingPlan)

