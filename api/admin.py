from django.contrib import admin
from .models import User, Research, Graph, Note, NodesNotesRelation


class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'last_name', 'first_name', 'surname', 'study_group', 'username', 'email', 'is_staff',
                    'is_active', 'last_login']
    ordering = ['last_name', 'first_name', 'surname']


class ResearchAdmin(admin.ModelAdmin):
    list_display = ['rsrch_id', 'title', 'description', 'start_date', 'end_date',
                    'get_researchers_ids']  # либо использовать researchers_names вместо researchers_ids


class GraphAdmin(admin.ModelAdmin):
    list_display = ['graph_id', 'data', 'title', 'research_id']


class NoteAdmin(admin.ModelAdmin):
    list_display = ['note_id', 'url', 'note_type', 'user_id']


class NodesNotesRelationAdmin(admin.ModelAdmin):
    list_display = ['id', 'node_id', 'note_id', 'graph_id']


admin.site.register(User, UserAdmin)
admin.site.register(Research, ResearchAdmin)
admin.site.register(Graph, GraphAdmin)
admin.site.register(Note, NoteAdmin)
admin.site.register(NodesNotesRelation, NodesNotesRelationAdmin)
