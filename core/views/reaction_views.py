from django.db import transaction
from django.db.models import F
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.response import Response
from ..permissions import IsAuthorOrReadOnly
from ..serializers import (
    ReactionSerializer,
)
from ..models import Comment, Post, Reaction


class ReactionViewSet(
    mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    serializer_class = ReactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]

    def get_queryset(self):
        return Reaction.objects.filter(author=self.request.user).select_related(
            "content_type"
        )

    def _change_reaction_count(self, content_type, object_id, amount):
        model_class = Post if content_type.model == "post" else Comment
        model_class.objects.filter(pk=object_id).update(
            reaction_count=F("reaction_count") + amount
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        content_type = serializer.validated_data["content_type"]
        object_id = serializer.validated_data["object_id"]
        reaction_type = serializer.validated_data["reaction_type"]

        with transaction.atomic():
            reaction, created = Reaction.objects.get_or_create(
                author=request.user,
                content_type=content_type,
                object_id=object_id,
                defaults={"reaction_type": reaction_type},
            )
            if created:
                self._change_reaction_count(content_type, object_id, 1)
            elif reaction.reaction_type != reaction_type:
                reaction.reaction_type = reaction_type
                reaction.save(update_fields=["reaction_type", "updated_at"])

        headers = self.get_success_headers(serializer.data)
        response_serializer = self.get_serializer(reaction)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
            headers=headers,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        content_type = instance.content_type
        object_id = instance.object_id
        self.perform_destroy(instance)
        self._change_reaction_count(content_type, object_id, -1)
        return Response(status=status.HTTP_204_NO_CONTENT)
