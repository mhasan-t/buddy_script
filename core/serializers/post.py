from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from ..models import Post, Reaction
from .user import UserSerializer
from .comment import CommentSerializer
from .post_image import PostImageSerializer


class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    images = PostImageSerializer(many=True, read_only=True)
    user_reaction = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "user",
            "content",
            "images",
            "is_public",
            "reaction_count",
            "comment_count",
            "user_reaction",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "reaction_count",
            "comment_count",
            "user_reaction",
            "created_at",
            "updated_at",
        ]

    def get_user_reaction(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return None

        content_type = ContentType.objects.get_for_model(Post)
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


class PostWithCommentsSerializer(PostSerializer):
    latest_comments = serializers.SerializerMethodField()

    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + ["latest_comments"]

    def get_latest_comments(self, obj):
        comments = obj.comments.filter(parent__isnull=True).order_by("-created_at")[:2]
        return CommentSerializer(comments, many=True, context=self.context).data
