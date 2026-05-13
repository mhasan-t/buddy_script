from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics, permissions, viewsets
from ..pagination import PlainCursorPagination
from ..permissions import IsAuthorOrReadOnly
from ..serializers import (
    CommentSerializer,
    PostSerializer,
    PostWithCommentsSerializer,
)
from ..models import Comment, Post, PostImage


@method_decorator(cache_page(10), name="dispatch")
class PublicPostListView(generics.ListAPIView):
    serializer_class = PostWithCommentsSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PlainCursorPagination

    def get_queryset(self):
        return (
            Post.objects.filter(is_public=True)
            .select_related("user")
            .prefetch_related("comments__user", "images")
            .order_by("-created_at")
        )


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]
    pagination_class = PlainCursorPagination

    def get_queryset(self):
        if self.action == "list":
            return (
                Post.objects.filter(user=self.request.user)
                .select_related("user")
                .prefetch_related("images")
                .order_by("-created_at")
            )
        return (
            Post.objects.filter(Q(is_public=True) | Q(user=self.request.user))
            .select_related("user")
            .prefetch_related("images")
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        post = serializer.save(user=self.request.user)

        # Handle image uploads
        uploaded_images = self.request.FILES.getlist("images")
        for image_file in uploaded_images:
            PostImage.objects.create(post=post, image=image_file)


@method_decorator(cache_page(10), name="dispatch")
class PostCommentsListAPIView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PlainCursorPagination

    def get_queryset(self):
        return (
            Comment.objects.filter(post_id=self.kwargs["post_pk"])
            .select_related("user", "parent")
            .order_by("created_at")
        )
