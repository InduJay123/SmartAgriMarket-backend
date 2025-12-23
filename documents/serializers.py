from rest_framework import serializers
from .models import PriceList

class PriceListSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.fullname', read_only=True)

    class Meta:
        model = PriceList
        fields = ['id', 'filename', 'file_url', 'upload_date', 'uploaded_by_name']
