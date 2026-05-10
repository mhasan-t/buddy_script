from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    CommentViewSet,
    PostCommentsListAPIView,
    PostViewSet,
    PublicPostListView,
    UserRegistrationView,
    ReactionViewSet,
)

router = DefaultRouter()
router.register('posts', PostViewSet, basename='post')
router.register('comments', CommentViewSet, basename='comment')
router.register('reactions', ReactionViewSet, basename='reaction')

urlpatterns = [
    path('auth/signup/', UserRegistrationView.as_view(), name='signup'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('posts/recent/', PublicPostListView.as_view(), name='public-post-list'),
    path('posts/<uuid:post_pk>/comments/', PostCommentsListAPIView.as_view(), name='post-comments'),
    path('', include(router.urls)),
]
