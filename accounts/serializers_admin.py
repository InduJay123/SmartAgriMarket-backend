from rest_framework import serializers
from .models import FarmerDetails, BuyerDetails


class FarmerAdminSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="user.id", read_only=True)
    profile_id = serializers.IntegerField(source="pk", read_only=True)
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    role = serializers.SerializerMethodField()
    account_status = serializers.SerializerMethodField()

    class Meta:
        model = FarmerDetails
        fields = [
            "id",
            "profile_id",
            "user_id",
            "role",
            "account_status",
            "email",
            "username",
            "fullname",
            "contact_number",
            "region",
            "farm_name",
            "address",
            "about",
            "profile_image",
            "is_active",
        ]

    def get_role(self, obj):
        return "Farmer"

    def get_account_status(self, obj):
        if obj.is_active:
            return "active"
        if obj.user.is_active:
            return "pending"
        return "rejected"


class BuyerAdminSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="user.id", read_only=True)
    profile_id = serializers.IntegerField(source="pk", read_only=True)
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    role = serializers.SerializerMethodField()
    account_status = serializers.SerializerMethodField()

    class Meta:
        model = BuyerDetails
        fields = [
            "id",
            "profile_id",
            "user_id",
            "role",
            "account_status",
            "email",
            "username",
            "fullname",
            "contact_number",
            "company_name",
            "company_email",
            "company_phone",
            "address",
            "city",
            "profile_image",
            "is_active",
        ]

    def get_role(self, obj):
        return "Buyer"

    def get_account_status(self, obj):
        if obj.is_active:
            return "active"
        if obj.user.is_active:
            return "pending"
        return "rejected"
