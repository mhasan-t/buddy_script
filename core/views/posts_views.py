from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics, permissions, viewsets
from ..pagination import RecentPostCursorPagination
from ..permissions import IsAuthorOrReadOnly
from ..serializers import (
    CommentSerializer,
    PostSerializer,
    PostWithCommentsSerializer,
)
from ..models import Comment, Post


@method_decorator(cache_page(30), name="dispatch")
class PublicPostListView(generics.ListAPIView):
    serializer_class = PostWithCommentsSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = RecentPostCursorPagination

    def get_queryset(self):
        return (
            Post.objects.filter(is_public=True)
            .select_related("user")
            .prefetch_related("comments__user")
            .order_by("-created_at")
        )


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]

    def get_queryset(self):
        if self.action == "list":
            return (
                Post.objects.filter(user=self.request.user)
                .select_related("user")
                .order_by("-created_at")
            )
        return (
            Post.objects.filter(Q(is_public=True) | Q(user=self.request.user))
            .select_related("user")
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@method_decorator(cache_page(10), name="dispatch")
class PostCommentsListAPIView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Comment.objects.filter(post_id=self.kwargs["post_pk"])
            .select_related("user", "parent")
            .order_by("created_at")
        )
