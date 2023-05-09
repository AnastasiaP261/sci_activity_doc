from django.contrib import admin
from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'last_name', 'first_name', 'surname', 'study_group', 'username', 'email', 'is_staff',
                    'is_active', 'last_login', 'get_groups']
    ordering = ['last_name', 'first_name', 'surname']


admin.site.register(User, UserAdmin)
