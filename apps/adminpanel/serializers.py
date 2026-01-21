from rest_framework import serializers
from apps.accounts.models import User

class PendingUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "phone",
            "role",
            "is_verified",
            "is_active",
        ]

class FarmerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "phone",
            "role",
            "is_verified",
            "is_active",
        ]

class BuyerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "phone",
            "role",
            "is_verified",
            "is_active",
        ]
