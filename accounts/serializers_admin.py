from rest_framework import serializers
from .models import ActivityLog, FarmerDetails, BuyerDetails


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


class ActivityLogSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    action = serializers.CharField(source="get_action_type_display", read_only=True)
    date = serializers.SerializerMethodField()
    timestamp = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = ActivityLog
        fields = [
            "id",
            "date",
            "timestamp",
            "action",
            "action_type",
            "module",
            "message",
            "user",
            "metadata",
        ]

    def get_user(self, obj):
        if obj.actor:
            return obj.actor.username
        return obj.actor_username or "System"

    def get_date(self, obj):
        return obj.created_at.date().isoformat()
