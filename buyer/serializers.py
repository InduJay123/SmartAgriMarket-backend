from rest_framework import serializers
from .models import Marketplace, Crop

class CropSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crop
        fields = ['crop_id', 'crop_name', 'description', 'image', 'category']


class MarketplaceSerializer(serializers.ModelSerializer):
    crop = CropSerializer()  # nested crop details

    class Meta:
        model = Marketplace
        fields = [
            'market_id',
            'farmer_id',
            'crop',
            'price',
            'unit',
            'predicted_date',
            'quantity',
            'farming_method',
            'region',
            'district',
            'image',
            'status'
        ]
