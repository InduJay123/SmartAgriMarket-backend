from rest_framework import serializers
from .models import Marketplace, Crop, User, Favourite, BuyerDetails

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
        img = obj.image or (obj.crop.image if obj.crop else None)

        if img is None:
            return None

        if isinstance(img, bytes):
            try:
                img = img.decode("utf-8")
            except UnicodeDecodeError:
                return None  # or str(img)

        # Handle string like "b'...'"
        if isinstance(img, str) and img.startswith("b'") and img.endswith("'"):
            img = img[2:-1]

        return img


    def get_farmer(self, obj):
        try:
            user = User.objects.get(user_id=obj.farmer_id)
            return FarmerSerializer(user).data
        except User.DoesNotExist:
            return None



class FarmerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'fullname', 'email', 'phone', 'region', 'created_at']


class FavouriteSerializer(serializers.ModelSerializer):
    market = MarketplaceSerializer(read_only=True)  # nest marketplace data

    class Meta:
        model = Favourite
        fields = ['id', 'user_id', 'market']


class BuyerProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.SerializerMethodField()
    fullname = serializers.CharField(source="user.fullname", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)
    phone = serializers.CharField(source="user.phone", read_only=True)

    class Meta:
        model = BuyerDetails
        fields = [
            "user_id",
            "fullname",
            "username",
            "email",
            "phone",
            "company_name",
            "company_email",
            "company_phone",
            "address",
            "city",
            "postal_code",
            "profile_image"
        ]
        
    def get_user_id(self, obj):
        return obj.user.user_id