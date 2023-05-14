from django.contrib import admin
from .models import Research, Graph, Note, NodesNotesRelation


# TODO: добавить множественные числа для админки


@admin.register(Research)
class ResearchAdmin(admin.ModelAdmin):
    list_display = ['rsrch_id', 'title', 'description', 'start_date', 'end_date',
                    'get_researchers_ids']  # либо использовать researchers_names вместо researchers_ids


@admin.register(Graph)
class GraphAdmin(admin.ModelAdmin):
    list_display = ['graph_id', 'data', 'title', 'research_id']


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['note_id', 'url', 'note_type', 'user_id']


@admin.register(NodesNotesRelation)
class NodesNotesRelationAdmin(admin.ModelAdmin):
    list_display = ['id', 'node_id', 'note_id', 'graph_id']
