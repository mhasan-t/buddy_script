from rest_framework import serializers
from ..models import Comment
from .user import UserSerializer


class LatestCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "user", "content", "created_at"]


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "post",
            "parent",
            "user",
            "content",
            "reaction_count",
            "reply_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "reaction_count",
            "reply_count",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        parent = attrs.get("parent")
        post = attrs.get("post")
        if parent and parent.post_id != post.id:
            raise serializers.ValidationError(
                "Parent comment must belong to the same post."
            )
        return attrs
