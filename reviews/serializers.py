from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            "id",
            "product",
            "user_name",
            "profile_image",
            "rating",
            "comment",
            "created_at"
        ]
       
    def get_user_name(self, obj):
        if hasattr(obj.user, "buyerdetails"):
            return obj.user.buyerdetails.fullname
        return obj.user.username

    def get_profile_image(self, obj):
        if hasattr(obj.user, "buyerdetails"):
            return obj.user.buyerdetails.profile_image
        return None