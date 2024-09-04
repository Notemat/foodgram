from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email')
    search_fields = ('username',)