from rest_framework import serializers
from .models import Cart
from crops.models import Crop

class CropSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crop
        fields = "__all__"

class CartSerializer(serializers.ModelSerializer):
    crop = CropSerializer(read_only=True)

    class Meta:
        model: Cart
        fields  = "__all__"