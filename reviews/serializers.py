from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.fullname', read_only=True)
    profile_image = serializers.CharField(source='user.buyer_details.profile_image', read_only=True)
    rating = serializers.IntegerField(required=False, min_value=0, max_value=5)

    class Meta:
        model = Review
        fields = ["id", "product", "user", "user_name",  "profile_image", "rating", "comment", "created_at"]