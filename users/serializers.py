from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from .models import User,FarmerDetails
from rest_framework_simplejwt.tokens import RefreshToken

class FarmerDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmerDetails
        fields = "__all__"

class UserProfileSerializer(serializers.ModelSerializer):
    farmer_details = FarmerDetailsSerializer(read_only=True)

    class Meta:
        model = User
        fields = "__all__"

class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields  = ["email", "username","fullname","password","role"]

    def validate(self, attrs):
        validate_password(attrs['password'])
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    role = serializers.CharField()

    def validate(self, attrs):
        #attrs is a dictionary of the data sent by the user
    
        #attrs.get("email") and attrs.get("password") are just extracting the
        # data sent by the user to pass it to Django’s authenticate.
        user = authenticate(
            email = attrs.get("email"),
            password=attrs.get("password")
        )

        if not user:
            raise serializers.ValidationError("Invalid Email or password")

        if user.role != attrs.get("role"):
            raise serializers.ValidationError(
                f"You are not a {attrs.get('role')}"
            )
            
        #refresh token (long-lived)
        #access token (short-lived)
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user":{
                "email": user.email,
                "username": user.username,
                "fullname": user.fullname,
                "role": user.role
            }
        }