from django.contrib import admin
from core.models import NodesNotesRelation, Note, Graph, Research, User
from django.contrib.auth.admin import UserAdmin
import gettext

from django.utils.translation import gettext  # обеспечивает локализацию
from django.utils.translation import gettext_lazy as _  # обеспечивает локализацию


# TODO: добавить множественные числа для админки


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ['id', 'last_name', 'first_name', 'surname', 'study_group', 'username', 'email', 'is_staff',
                    'is_active', 'last_login', 'get_groups_str']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('last_name', 'first_name', 'surname', 'email')}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                ),
            },
        ),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_filter = ('study_group', 'groups', 'is_active', 'is_staff', 'is_superuser',)
    search_fields = ('username', 'first_name', 'last_name', 'surname', 'email')


@admin.register(Research)
class ResearchAdmin(admin.ModelAdmin):
    list_display = ['rsrch_id', 'title', 'description', 'start_date', 'end_date',
                    'get_rsrchers_ids']  # либо использовать researchers_names вместо rsrchers_ids
    search_fields = ['title']


@admin.register(Graph)
class GraphAdmin(admin.ModelAdmin):
    list_display = ['graph_id', 'data', 'title', 'rsrch_id']
    date_hierarchy = 'nodesnotesrelation__note_id__created_at'
    list_filter = ('rsrch_id',)
    search_fields = ['title']


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['note_id', 'url', 'note_type', 'user_id', 'created_at', 'rsrch_id']
    date_hierarchy = 'created_at'  # навигация по детализации на основе даты по этому полю
    list_filter = ('rsrch_id', 'user_id', 'note_type')


@admin.register(NodesNotesRelation)
class NodesNotesRelationAdmin(admin.ModelAdmin):
    list_display = ['id', 'node_id', 'note_id', 'graph_id']
