from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ['id', 'last_name', 'first_name', 'surname', 'study_group', 'username', 'email', 'is_staff',
                    'is_active', 'last_login', 'get_groups']
    ordering = ['last_name', 'first_name', 'surname']
