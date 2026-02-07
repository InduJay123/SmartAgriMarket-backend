from rest_framework import serializers
from .models import FarmerDetails, BuyerDetails

class FarmerAdminSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    role = serializers.SerializerMethodField()

    class Meta:
        model = FarmerDetails
        fields = [
            "id",
            "user_id",
            "role",
            "email",
            "username",
            "fullname",
            "contact_number",
            "region",
            "farm_name",
            "address",
            "about",
            "is_active",
        ]

    def get_role(self, obj):
        return "Farmer"


class BuyerAdminSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    role = serializers.SerializerMethodField()

    class Meta:
        model = BuyerDetails
        fields = [
            "id",
            "user_id",
            "role",
            "email",
            "username",
            "fullname",
            "contact_number",
            "company_name",
            "company_email",
            "company_phone",
            "address",
            "city",
            "is_active",
        ]

    def get_role(self, obj):
        return "Buyer"
