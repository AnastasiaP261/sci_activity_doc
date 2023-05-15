from rest_framework import serializers
from core.models import Research, Graph, Note, NodesNotesRelation, User


class CustomUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        lookup_field = 'username'
        fields = ('username', 'last_name', 'first_name', 'surname', 'study_group', 'email', 'is_staff',
                  'is_active', 'last_login')


class ResearchSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Research
        fields = ('rsrch_id', 'title', 'description', 'start_date', 'end_date',
                  'get_researchers_ids')


class GraphSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Graph
        fields = ('graph_id', 'data', 'title', 'research_id')


class NoteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Note
        fields = ('note_id', 'url', 'note_type', 'user_id')


class NodesNotesRelationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = NodesNotesRelation
        fields = ('id', 'node_id', 'note_id', 'graph_id')
