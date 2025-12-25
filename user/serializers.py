from rest_framework import serializers
from .models import Users,FarmerDetails
     
class FarmerDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmerDetails
        fields = "__all__"

class UserProfileSerializer(serializers.ModelSerializer):
    farmer_details = FarmerDetailsSerializer(read_only=True)

    class Meta:
        model = Users
        fields = "__all__"