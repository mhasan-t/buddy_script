from django.db import models
from .base import BaseModel
from .post import Post


class PostImage(BaseModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="posts/")

    class Meta:
        db_table = "post_images"
        indexes = [
            models.Index(fields=["post"]),
        ]

    def __repr__(self):
        return f"PostImage(post_id={self.post_id}, image={self.image})"
