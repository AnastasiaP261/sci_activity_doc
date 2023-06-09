from rest_framework import serializers

from latex2html.models import RemakeItem


class RemakeItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = RemakeItem
        fields = ('id', 'title', 'description', 'latex_reqex', 'html_format_str', 'child_item', 'is_head')
        extra_kwargs = {
            'id': {
                'read_only': True,
            },
        }
