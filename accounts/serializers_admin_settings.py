from rest_framework import serializers
from django.contrib.auth.models import User
from .models_admin import AdminProfile

class AdminSettingsSerializer(serializers.Serializer):
    full_name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    email_notifications = serializers.BooleanField(required=False)
    price_alert_notifications = serializers.BooleanField(required=False)
    system_update_notifications = serializers.BooleanField(required=False)

    def update(self, instance, validated_data):
        # instance = (user, profile)
        user, profile = instance

        # User fields
        if "full_name" in validated_data:
            full_name = validated_data.get("full_name", user.username)
            parts = full_name.split(" ", 1)
            user.first_name = parts[0] if parts else ""
            user.last_name = parts[1] if len(parts) > 1 else ""
        if "email" in validated_data:
            user.email = validated_data.get("email", user.email)
        user.save()

        # Profile fields
        if "phone" in validated_data:
            profile.phone = validated_data.get("phone")
        if "email_notifications" in validated_data:
            profile.email_notifications = validated_data["email_notifications"]
        if "price_alert_notifications" in validated_data:
            profile.price_alert_notifications = validated_data["price_alert_notifications"]
        if "system_update_notifications" in validated_data:
            profile.system_update_notifications = validated_data["system_update_notifications"]
        profile.save()

        return (user, profile)
