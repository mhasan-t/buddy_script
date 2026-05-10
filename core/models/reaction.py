from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from .base import BaseModel
from .user import User


class Reaction(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')
    reaction_type = models.CharField(max_length=20, default='like')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reactions'
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['author']),
        ]
        unique_together = ('author', 'content_type', 'object_id')

    def __repr__(self):
        return super().__repr__() + f" (author_id={self.author_id}, content_type_id={self.content_type_id}, object_id={self.object_id}, reaction_type={self.reaction_type})"