from django.db import models
from .base import BaseModel
from .user import User


class Post(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)
    reaction_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)

    class Meta:
        db_table = "posts"
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["is_public", "-created_at"]),
        ]

    def __repr__(self):
        return f"Post(user_id={self.user_id}, content={self.content[:20]}..., is_public={self.is_public}, reaction_count={self.reaction_count}, comment_count={self.comment_count})"
