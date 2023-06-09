from django.contrib import admin

from .models import RemakeItem


@admin.register(RemakeItem)
class RemakeItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'latex_reqex', 'html_format_str', 'child_item', 'is_head']
    search_fields = ['title', 'latex_reqex', 'html_format_str']
    list_filter = ['is_head',]
