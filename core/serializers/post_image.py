from rest_framework import serializers
from ..models import PostImage


class PostImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = PostImage
        fields = ["id", "image_url", "created_at"]
        read_only_fields = ["id", "created_at"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and hasattr(obj.image, "url"):
            url = obj.image.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None
