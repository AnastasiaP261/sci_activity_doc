from django.contrib import admin
from core.models import NodesNotesRelation, Note, Graph, Research, User
from django.contrib.auth.admin import UserAdmin


# TODO: добавить множественные числа для админки


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ['id', 'last_name', 'first_name', 'surname', 'study_group', 'username', 'email', 'is_staff',
                    'is_active', 'last_login', 'get_groups_str']
    ordering = ['last_name', 'first_name', 'surname']


@admin.register(Research)
class ResearchAdmin(admin.ModelAdmin):
    list_display = ['rsrch_id', 'title', 'description', 'start_date', 'end_date',
                    'get_rsrchers_ids']  # либо использовать researchers_names вместо rsrchers_ids


@admin.register(Graph)
class GraphAdmin(admin.ModelAdmin):
    list_display = ['graph_id', 'data', 'title', 'rsrch_id']


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['note_id', 'url', 'note_type', 'user_id']


@admin.register(NodesNotesRelation)
class NodesNotesRelationAdmin(admin.ModelAdmin):
    list_display = ['id', 'node_id', 'note_id', 'graph_id']
