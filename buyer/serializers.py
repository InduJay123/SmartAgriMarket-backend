from rest_framework import serializers
from .models import Marketplace, Crop, User

class CropSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crop
        fields = ['crop_id', 'crop_name', 'description', 'image', 'category']


class MarketplaceSerializer(serializers.ModelSerializer):
    crop = CropSerializer(read_only=True)
    crop_name = serializers.SerializerMethodField()
    crop_default_image = serializers.CharField(source="crop.image", read_only=True)
    image_url = serializers.SerializerMethodField() 
    farmer = serializers.SerializerMethodField()

    class Meta:
        model = Marketplace
        fields = "__all__"

    def get_crop_name(self,obj):
        try:
            return obj.crop.crop_name if obj.crop else None
        except Crop.DoesNotExist:
            return None

    def get_image_url(self, obj):
        """
        Return farmer's image if available, otherwise crop's default image.
        Clean up byte string representation if necessary.
        """
        img = obj.image or obj.crop.image
        if img:
            # Remove b'...' wrapper if present
            if isinstance(img, str) and img.startswith("b'") and img.endswith("'"):
                img = img[2:-1]
            return img
        return None

    def get_farmer(self, obj):
        try:
            user = User.objects.get(user_id=obj.farmer_id)
            return FarmerSerializer(user).data
        except User.DoesNotExist:
            return None



class FarmerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'name', 'email', 'phone', 'region', 'profile_image', 'created_at']

