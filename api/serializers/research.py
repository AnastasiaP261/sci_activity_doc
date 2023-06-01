from rest_framework import serializers

from api.serializers.user import UserSerializer
from core.models import Research


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
