from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType

from core.models.reaction import Reaction
from ..models import Comment
from .user import UserSerializer


class LatestCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "user", "content", "created_at"]


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_reaction = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "post",
            "parent",
            "user",
            "content",
            "reaction_count",
            "user_reaction",
            "reply_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "reaction_count",
            "user_reaction",
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

    def get_user_reaction(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return None

        content_type = ContentType.objects.get_for_model(Comment)
        reaction = Reaction.objects.filter(
            author=request.user,
            content_type=content_type,
            object_id=obj.id,
        ).first()
        if not reaction:
            return None

        return {
            "id": reaction.id,
            "reaction_type": reaction.reaction_type,
        }
