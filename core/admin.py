from django.contrib import admin
from .models import Research, Graph, Note, NodesNotesRelation


# TODO: добавить множественные числа для админки

class ResearchAdmin(admin.ModelAdmin):
    list_display = ['rsrch_id', 'title', 'description', 'start_date', 'end_date',
                    'get_researchers_ids']  # либо использовать researchers_names вместо researchers_ids


class GraphAdmin(admin.ModelAdmin):
    list_display = ['graph_id', 'data', 'title', 'research_id']


class NoteAdmin(admin.ModelAdmin):
    list_display = ['note_id', 'url', 'note_type', 'user_id']


class NodesNotesRelationAdmin(admin.ModelAdmin):
    list_display = ['id', 'node_id', 'note_id', 'graph_id']


admin.site.register(Research, ResearchAdmin)
admin.site.register(Graph, GraphAdmin)
admin.site.register(Note, NoteAdmin)
admin.site.register(NodesNotesRelation, NodesNotesRelationAdmin)
