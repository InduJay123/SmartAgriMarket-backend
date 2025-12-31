# accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import FarmerDetails, BuyerDetails

class SignupSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=["Farmer", "Buyer"])
    fullname = serializers.CharField(write_only=True, required=True)
    contact_number = serializers.CharField(write_only=True, required=False)
    farm_name = serializers.CharField(write_only=True, required=False)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value

    def create(self, validated_data):
        role = validated_data.pop("role")
        fullname = validated_data.pop("fullname", "")
        contact_number = validated_data.pop("contact_number", "")
        farm_name = validated_data.pop("farm_name", "")

        user = User.objects.create_user(**validated_data)

        if role == "Farmer":
            FarmerDetails.objects.create(
                user=user,
                fullname=fullname,
                contact_number=contact_number,
                farm_name=farm_name,
            )
        elif role == "Buyer":
            BuyerDetails.objects.create(
                user=user,
                fullname=fullname,
                contact_number=contact_number,
            )

        return user