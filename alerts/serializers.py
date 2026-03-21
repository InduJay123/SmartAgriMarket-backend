from rest_framework import serializers
from .models import UserAlertState

class UserAlertSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='alert.category')
    message = serializers.CharField(source='alert.message')

    class Meta:
        model = UserAlertState
        fields = ['id', 'category', 'message']  # include other fields if needed
