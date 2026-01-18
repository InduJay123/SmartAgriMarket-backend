from rest_framework import serializers
from .models import UserAlert

class UserAlertSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='alert.category')
    message = serializers.CharField(source='alert.message')

    class Meta:
        model = UserAlert
        fields = ['id', 'category', 'message']  # include other fields if needed
