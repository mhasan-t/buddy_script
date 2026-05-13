from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    CommentViewSet,
    CommentRepliesListAPIView,
    PostCommentsListAPIView,
    PostViewSet,
    PublicPostListView,
    UserRegistrationView,
    LoginView,
    RefreshTokenView,
    LogoutView,
    LogoutAllView,
    ReactionViewSet,
)

router = DefaultRouter()
router.register("posts", PostViewSet, basename="post")
router.register("comments", CommentViewSet, basename="comment")
router.register("reactions", ReactionViewSet, basename="reaction")

urlpatterns = [
    path("auth/signup/", UserRegistrationView.as_view(), name="signup"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/refresh/", RefreshTokenView.as_view(), name="token_refresh"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/logout-all/", LogoutAllView.as_view(), name="logout_all"),
    path("posts/recent/", PublicPostListView.as_view(), name="public-post-list"),
    path(
        "posts/<uuid:post_pk>/comments/",
        PostCommentsListAPIView.as_view(),
        name="post-comments",
    ),
    path(
        "comments/<uuid:comment_pk>/replies/",
        CommentRepliesListAPIView.as_view(),
        name="comment-replies",
    ),
    path("", include(router.urls)),
]
