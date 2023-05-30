from rest_framework import serializers
from core.models import Research, Graph, Note, NodesNotesRelation, User
from rest_framework.validators import UniqueTogetherValidator


class CustomUserSerializer(serializers.HyperlinkedModelSerializer):
    groups = serializers.ListField(
        child=serializers.CharField(min_length=1),
        allow_empty=True,
        read_only=True,
        allow_null=True,
        source='get_groups_list'
    )

    class Meta:
        model = User
        lookup_field = 'username'
        fields = ('id', 'username', 'last_name', 'first_name', 'surname', 'study_group', 'email', 'is_staff',
                  'is_active', 'last_login', 'groups')
        extra_kwargs = {
            'id': {
                'read_only': True,
            },
        }


class ResearchSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Research
        fields = ('rsrch_id', 'title', 'description', 'start_date', 'end_date',
                  'get_researchers_ids')


class RawNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        lookup_field = 'note_id'
        fields = ('note_id', 'url', 'note_type', 'user_id', 'research_id')


class NoteSerializer(serializers.Serializer):
    note_id = serializers.IntegerField(min_value=1, allow_null=False, source='note_id_id', read_only=True)
    url = serializers.URLField(allow_blank=False, allow_null=False, source='note_id.url', required=True)
    note_type = serializers.CharField(min_length=2, allow_null=False, allow_blank=False, source='note_id.note_type',
                                      required=False)
    created_at = serializers.DateTimeField(allow_null=False, source='note_id.created_at', read_only=True)
    research_id = serializers.IntegerField(min_value=1, allow_null=False, source='note_id.research_id_id',
                                           required=True)
    graph_id = serializers.IntegerField(source='graph_id_id', required=False)


class NoteWithAuthorInfoSerializer(NoteSerializer):
    author = CustomUserSerializer(source='note_id.user_id', required=True)


class NoteWithAuthorIDAndNodeIDSerializer(NoteSerializer):
    author_user_id = serializers.IntegerField(allow_null=False, source='note_id.user_id_id', required=True)
    node_id = serializers.CharField(required=False)


class NodesNotesRelationSerializer(serializers.ModelSerializer):
    note_id = serializers.IntegerField(min_value=1, allow_null=False, source='note_id_id', read_only=True)

    class Meta:
        model = NodesNotesRelation
        lookup_field = 'graph_id'
        fields = ['node_id', 'note_id']


class GraphSerializer(serializers.HyperlinkedModelSerializer):
    research_id = serializers.IntegerField(min_value=1, allow_null=False, source='research_id_id')

    raw_data = serializers.CharField(allow_null=False, allow_blank=False, source='data')

    levels = serializers.JSONField(read_only=True, source='dot_to_json_levels')
    nodes_metadata = serializers.JSONField(read_only=True, source='get_nodes_metadata_json')

    class Meta:
        model = Graph
        lookup_field = 'graph_id'
        fields = ['graph_id', 'title', 'research_id', 'raw_data', 'levels', 'nodes_metadata']


class GraphLevelsSerializer(serializers.ModelSerializer):
    levels = serializers.JSONField(allow_null=False, read_only=True, source='dot_to_json_levels')

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    class Meta:
        model = Graph
        lookup_field = 'graph_id'
        fields = ['graph_id', 'levels']


class NodeMetadataSerializer(serializers.Serializer):
    is_subgraph = serializers.BooleanField(allow_null=False)
    subgraph_graph_id = serializers.IntegerField(min_value=0)
    notes_ids = serializers.ListField(child=serializers.IntegerField(min_value=0), allow_empty=True, allow_null=False)
    title = serializers.CharField(allow_null=False, allow_blank=True)

    def validate_subgraph_graph_id(self, value):
        if value < 0:
            raise serializers.ValidationError("subgraph_graph_id must be a non-negative integer")

        if not Graph.objects.filter(graph_id=value).exists():
            raise serializers.ValidationError("there is no graph with such id")

    def validate_notes_ids(self, value):
        if len(value) > 0:
            if not Note.objects.filter(pk__in=value).exists():
                raise serializers.ValidationError("no notes with such ids")


class GraphMetadataSerializer(serializers.ModelSerializer):
    node_metadata = NodeMetadataSerializer()
    node_id = serializers.CharField(allow_null=False, allow_blank=False)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    class Meta:
        model = Graph
        lookup_field = 'graph_id'
        fields = ['graph_id', 'node_metadata', 'node_id']


class GraphNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Graph
        lookup_field = 'graph_id'
        fields = ['graph_id', 'title']
