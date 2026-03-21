from rest_framework import serializers
from .models import PriceUpload

class PriceUploadSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = PriceUpload
        fields = ["id", "original_name", "status", "processed_rows", "error_message", "created_at", "file_url"]

    def get_file_url(self, obj):
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url
