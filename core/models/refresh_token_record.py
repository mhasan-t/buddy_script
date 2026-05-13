from django.db import models
from .base import BaseModel
from .user import User


class RefreshTokenRecord(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="refresh_token_records"
    )
    jti = models.CharField(max_length=255, unique=True)
    expires_at = models.DateTimeField()
    revoked = models.BooleanField(default=False)
    device_info = models.CharField(max_length=512, blank=True, null=True)

    class Meta:
        db_table = "refresh_token_records"
