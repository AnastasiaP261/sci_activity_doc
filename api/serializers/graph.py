from rest_framework import serializers

from api.serializers import NodeMetadataUpdateSerializer
from core.models import Graph


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
