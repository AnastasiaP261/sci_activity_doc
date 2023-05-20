from rest_framework import serializers
from core.models import Research, Graph, Note, NodesNotesRelation, User


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


class GraphSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Graph
        fields = ('graph_id', 'data', 'title', 'research_id')


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


class NoteFullInfoSerializer(NoteSerializer):
    author = CustomUserSerializer(source='note_id.user_id', required=True)


class NoteShortInfoSerializer(NoteSerializer):
    author_user_id = serializers.IntegerField(allow_null=False, source='note_id.user_id_id', required=True)
    node_id = serializers.CharField(write_only=True, required=False)
