from django.db import models
from .base import BaseModel
from .user import User
from .post import Post


class Comment(BaseModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    content = models.TextField()
    reaction_count = models.IntegerField(default=0)
    reply_count = models.IntegerField(default=0)

    class Meta:
        db_table = 'comments'
        indexes = [
            models.Index(fields=['post']),
            models.Index(fields=['parent']),
            models.Index(fields=['-created_at']),
        ]
    
    def __repr__(self):
        return f" (post_id={self.post_id}, user_id={self.user_id}, parent_id={self.parent_id}), content={self.content[:20]}..., reaction_count={self.reaction_count})"