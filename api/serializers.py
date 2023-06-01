from rest_framework import serializers

from core.models import NodesNotesRelation, Note, Graph, Research, User


class UserSerializer(serializers.ModelSerializer):
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


class GraphSerializer(serializers.ModelSerializer):
    raw_data = serializers.CharField(allow_null=False, allow_blank=False, source='data', read_only=True)

    levels = serializers.JSONField(read_only=True, source='dot_to_json_levels')
    nodes_metadata = serializers.JSONField(read_only=True, source='get_nodes_metadata_json')

    class Meta:
        model = Graph
        lookup_field = 'graph_id'
        fields = ['graph_id', 'title', 'rsrch_id', 'raw_data', 'levels', 'nodes_metadata']
        extra_kwargs = {
            'graph_id': {
                'read_only': True,
            },
        }


class GraphLevelsUpdateSerializer(serializers.ModelSerializer):
    levels = serializers.JSONField(allow_null=False, source='dot_to_json_levels')

    def update(self, instance, validated_data):
        if 'levels' in validated_data:
            instance.rewrite_graph_schema(validated_data.get('levels'))
            instance.save()
        return instance

    class Meta:
        model = Graph
        lookup_field = 'graph_id'
        fields = ['graph_id', 'levels']
        extra_kwargs = {
            'graph_id': {
                'read_only': True,
            },
        }


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


class GraphMetadataUpdateSerializer(serializers.ModelSerializer):
    node_metadata = NodeMetadataUpdateSerializer()
    node_id = serializers.CharField(allow_null=False, allow_blank=False)

    def update(self, instance, validated_data):
        if 'node_id' in validated_data and 'node_metadata' in validated_data:
            instance.rewrite_node_metadata(
                validated_data.get('node_id'),
                validated_data.get('node_metadata'),
            )
            instance.save()

        return super().update(instance, validated_data)

    class Meta:
        model = Graph
        lookup_field = 'graph_id'
        fields = ['graph_id', 'node_metadata', 'node_id']

        extra_kwargs = {
            'graph_id': {
                'read_only': True,
            },
        }


class GraphTitleUpdateSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        if 'title' in validated_data:
            instance.title = validated_data.get('title')
            instance.save()
        return instance

    class Meta:
        model = Graph
        lookup_field = 'graph_id'
        fields = ['graph_id', 'title']

        extra_kwargs = {
            'graph_id': {
                'read_only': True,
            },
        }


class ResearchSerializer(serializers.ModelSerializer):
    researchers = UserSerializer(many=True, allow_null=False, read_only=True)

    class Meta:
        model = Research
        fields = (
            'rsrch_id', 'title', 'description', 'start_date', 'end_date', 'created_at', 'researchers')
        extra_kwargs = {
            'rsrch_id': {
                'read_only': True,
            },
            'created_at': {
                'read_only': True,
            },
        }


class ResearchCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Research
        fields = ('rsrch_id', 'title', 'description', 'start_date', 'end_date')


class ResearchUpdateSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.start_date = validated_data.get('start_date', instance.start_date)
        instance.end_date = validated_data.get('end_date', instance.end_date)
        if 'researchers' in validated_data:
            instance.researchers.set(validated_data.get('researchers'))
        instance.save()
        return instance

    class Meta:
        model = Research
        fields = ('title', 'description', 'start_date', 'end_date', 'researchers')
        extra_kwargs = {
            'researchers': {
                'allow_empty': True,
            },
        }
