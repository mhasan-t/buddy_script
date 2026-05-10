from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from ..models import Post, Comment, Reaction
from .user import AuthorSerializer


class ReactionSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    target_type = serializers.CharField(write_only=True)
    target_id = serializers.UUIDField(write_only=True)
    target = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Reaction
        fields = [
            'id',
            'author',
            'target_type',
            'target_id',
            'target',
            'reaction_type',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'author', 'target', 'created_at', 'updated_at']

    def get_target(self, obj):
        return obj.content_type.model if obj.content_type else None

    def validate(self, attrs):
        target_type = attrs.pop('target_type', None)
        target_id = attrs.pop('target_id', None)
        if target_type not in ('post', 'comment'):
            raise serializers.ValidationError({'target_type': 'Must be either post or comment.'})

        model_cls = Post if target_type == 'post' else Comment
        if not model_cls.objects.filter(pk=target_id).exists():
            raise serializers.ValidationError({'target_id': 'Target object does not exist.'})

        attrs['content_type'] = ContentType.objects.get_for_model(model_cls)
        attrs['object_id'] = target_id
        return attrs
