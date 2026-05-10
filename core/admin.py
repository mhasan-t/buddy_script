from django.contrib import admin
from .models.user import User
from .models.post import Post
from .models.comment import Comment
from .models.reaction import Reaction

admin.site.register(User)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Reaction)

