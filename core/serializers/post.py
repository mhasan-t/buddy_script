from rest_framework import serializers
from ..models import Post
from .user import AuthorSerializer
from .comment import LatestCommentSerializer


class PostSerializer(serializers.ModelSerializer):
    user = AuthorSerializer(read_only=True)

    class Meta:
        model = Post
        fields = [
            'id',
            'user',
            'content',
            'image_url',
            'is_public',
            'reaction_count',
            'comment_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'reaction_count', 'comment_count', 'created_at', 'updated_at']


class PostWithCommentsSerializer(PostSerializer):
    latest_comments = serializers.SerializerMethodField()

    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + ['latest_comments']

    def get_latest_comments(self, obj):
        comments = obj.comments.filter(parent__isnull=True).order_by('-created_at')[:2]
        return LatestCommentSerializer(comments, many=True).data
