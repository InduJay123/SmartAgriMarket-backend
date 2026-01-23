from rest_framework import serializers
from .models import FarmerDetails, BuyerDetails

class FarmerAdminSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = FarmerDetails
        fields = [
            "id", "user_id","username", "email",
            "fullname", "farm_name", "contact_number", "region",
            "is_active", "deactivate_at",
        ]


class BuyerAdminSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = BuyerDetails
        fields = [
            "id", "user_id","username", "email",
            "fullname", "contact_number", "company_name",
            "city", "is_active", "deactivate_at",
        ]