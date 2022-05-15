from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):

    model = CustomUser
    list_display = (
        'pk',
        'username',
        'email',
        'bio',
        'role')
    search_fields = ('username',)
    list_filter = ('username',)
    empty_value_display = '-пусто-'
