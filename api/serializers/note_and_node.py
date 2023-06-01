from rest_framework import serializers

from api.serializers.user import UserSerializer
from core.models import Note, NodesNotesRelation, Graph


class NoteWithoutGraphInfoSerializer(serializers.ModelSerializer):
    rsrch_id = serializers.IntegerField(min_value=1, allow_null=False, source='rsrch_id_id', read_only=True)
    user_id = serializers.IntegerField(min_value=1, allow_null=False, source='user_id_id')

    class Meta:
        model = Note
        fields = ('note_id', 'url', 'note_type', 'created_at', 'rsrch_id', 'user_id',)
        extra_kwargs = {
            'note_id': {
                'read_only': True,
            },
        }


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        extra_kwargs = {
            'note_id': {
                'read_only': True,
            },
            'created_at': {
                'read_only': True,
            },
            'note_type': {
                'required': False,
            },
        }
        fields = ('note_id', 'url', 'note_type', 'created_at', 'rsrch_id')


class NodesNotesRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = NodesNotesRelation
        fields = ('node_id', 'graph_id', 'note_id')
        extra_kwargs = {
            'note_id': {
                'read_only': True,
            },
        }


class NoteWithAuthorInfoSerializer(serializers.ModelSerializer):
    author = UserSerializer(source='user_id', read_only=True)
    graphs_info = NodesNotesRelationSerializer(required=False, many=True, source='nodesnotesrelation_set')

    class Meta:
        model = Note
        extra_kwargs = {
            'note_id': {
                'read_only': True,
            },
            'created_at': {
                'read_only': True,
            },
            'note_type': {
                'required': False,
            },
        }
        fields = ('note_id', 'url', 'note_type', 'created_at', 'rsrch_id', 'author', 'graphs_info')


class NodeMetadataUpdateSerializer(serializers.Serializer):
    is_subgraph = serializers.BooleanField(allow_null=False)
    subgraph_graph_id = serializers.IntegerField(min_value=0, allow_null=False)
    notes_ids = serializers.ListField(child=serializers.IntegerField(min_value=0), required=False, allow_empty=True)
    title = serializers.CharField(allow_null=False, allow_blank=True)

    def update(self, instance, validated_data):
        # потому что обновление происходит через наследника (см GraphMetadataUpdateSerializer)
        pass

    def validate_subgraph_graph_id(self, value):
        if value < 0:
            raise serializers.ValidationError("subgraph_graph_id must be a non-negative integer")

        if not Graph.objects.filter(graph_id=value).exists():
            raise serializers.ValidationError("there is no graph with such id")

        return value

    def validate_notes_ids(self, value):
        if len(value) > 0:
            if not Note.objects.filter(pk__in=value).exists():
                raise serializers.ValidationError("no notes with such ids")
        return value
