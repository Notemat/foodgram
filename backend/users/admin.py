from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    search_fields = ('username', 'email')
    fieldsets = (
        (None, {
            'fields': (
                ('is_staff', 'is_active'),
                'is_superuser',
                ('date_joined', 'last_login'),
                'groups',
                'user_permissions',
                ('username', 'password'),
                ('first_name', 'last_name'),
                'avatar',
                'email'
            ),
        }),
    )
