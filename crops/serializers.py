from rest_framework import serializers
from .models import Crop, Marketplace

class CropSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crop
        fields = ['crop_id', 'crop_name', 'description']

class MarketplaceSerializer(serializers.ModelSerializer):   
    crop_name = serializers.SerializerMethodField()
    crop_default_image = serializers.CharField(source="crop.image", read_only=True)
    image_url = serializers.SerializerMethodField() 

    class Meta:
        model = Marketplace
        fields = "__all__"

    def get_crop_name(self,obj):
        try:
            return obj.crop.crop_name if obj.crop else None
        except Crop.DoesNotExist:
            return None  
    
    def get_image_url(self, obj):
        # Adjust this depending on your model's image field
        try:
            if obj.image:  # or obj.crop.image if the image is on the related crop
                return obj.image.url  # If it's an ImageField/FileField
            return None
        except AttributeError:
            return None