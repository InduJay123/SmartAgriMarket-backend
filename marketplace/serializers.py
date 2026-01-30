from rest_framework import serializers
from .models import Crop, Marketplace, Favourite
from django.contrib.auth.models import User

class FarmerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['fullname', 'profile_image', 'farm_name', 'contact_number', 'region', 'address', 'about']

class CropSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crop
        fields = "__all__"


class MarketplaceSerializer(serializers.ModelSerializer):
    crop = CropSerializer(read_only=True)
    crop_name = serializers.CharField(source="crop.crop_name", read_only=True)
    crop_default_image = serializers.CharField(source="crop.image", read_only=True)
    farmer = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    image = serializers.URLField(required=False, allow_null=True)

    class Meta:
        model = Marketplace
        fields = "__all__"
        read_only_fields = ['farmer_id']

    def get_farmer(self, obj):
        try:
            user = User.objects.get(id=obj.farmer_id)
            farmer_details = getattr(user, 'farmerdetails', None)
            data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'fullname': farmer_details.fullname if farmer_details else None,
                'profile_image': farmer_details.profile_image if farmer_details else None,
                'region': farmer_details.region if farmer_details else None,
                'contact_number': farmer_details.contact_number if farmer_details else None,
                'farm_name': farmer_details.farm_name if farmer_details else None,
                'about': farmer_details.about if farmer_details else None,
                'date_joined': user.date_joined,  
            }
            return data
        except User.DoesNotExist:
            return None

    def get_image_url(self, obj):
        return obj.image or (obj.crop.image if obj.crop else None)


class FavouriteSerializer(serializers.ModelSerializer):
    market = MarketplaceSerializer(read_only=True)

    class Meta:
        model = Favourite
        fields = ['id', 'market']
