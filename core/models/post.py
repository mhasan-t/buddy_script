from django.db import models
from .base import BaseModel
from .user import User


class Post(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to="posts/", blank=True, null=True)
    image_url = models.URLField(blank=True)
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
        return f" (user_id={self.user_id}, content={self.content[:20]}..., image_url={self.image_url}, is_public={self.is_public}, reaction_count={self.reaction_count}, comment_count={self.comment_count})"
