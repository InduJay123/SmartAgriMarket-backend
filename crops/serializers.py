from rest_framework import serializers
from .models import Crop, Marketplace

class CropSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crop
        fields = ['crop_id', 'crop_name', 'description']

class MarketplaceSerializer(serializers.ModelSerializer):
    
    crop_name = serializers.SerializerMethodField()

    class Meta:
        model = Marketplace
        fields = "__all__"

    def get_crop_name(self,obj):
        try:
            return obj.crop.crop_name if obj.crop else None
        except Crop.DoesNotExist:
            return None