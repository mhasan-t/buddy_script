from django.db import transaction
from django.db.models import F, Q
from rest_framework import permissions, viewsets

from core.pagination import PlainCursorPagination
from ..permissions import IsAuthorOrReadOnly
from ..serializers import (
    CommentSerializer,
)
from ..models import Comment, Post
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics, permissions, viewsets
from ..pagination import PlainCursorPagination
from ..permissions import IsAuthorOrReadOnly
from ..serializers import (
    CommentSerializer,
)
from ..models import Comment, Post


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]
    pagination_class = PlainCursorPagination

    def get_queryset(self):
        queryset = Comment.objects.select_related("user", "post", "parent").order_by(
            "created_at"
        )
        if self.action == "list":
            queryset = queryset.filter(
                Q(post__is_public=True) | Q(user=self.request.user)
            )
        post_id = self.request.query_params.get("post_id")
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        return queryset

    def perform_create(self, serializer):
        with transaction.atomic():
            comment = serializer.save(user=self.request.user)
            if comment.parent_id:
                Comment.objects.filter(pk=comment.parent_id).update(
                    reply_count=F("reply_count") + 1
                )
            else:
                Post.objects.filter(pk=comment.post_id).update(
                    comment_count=F("comment_count") + 1
                )

    def perform_destroy(self, instance):
        target = instance.parent_id or instance.post_id
        is_reply = bool(instance.parent_id)
        with transaction.atomic():
            super().perform_destroy(instance)
            if is_reply:
                Comment.objects.filter(pk=target).update(
                    reply_count=F("reply_count") - 1
                )
            else:
                Post.objects.filter(pk=target).update(
                    comment_count=F("comment_count") - 1
                )


@method_decorator(cache_page(10), name="dispatch")
class CommentRepliesListAPIView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PlainCursorPagination

    def get_queryset(self):
        return (
            Comment.objects.filter(parent_id=self.kwargs["comment_pk"])
            .select_related("user", "parent", "post")
            .filter(Q(post__is_public=True) | Q(user=self.request.user))
            .order_by("created_at")
        )
