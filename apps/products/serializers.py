from rest_framework import serializers
from .models import Product, Listing
from apps.accounts.serializers import UserSerializer

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','name','category','default_unit','image']

class ListingSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product', write_only=True)
    seller = UserSerializer(read_only=True)

    class Meta:
        model = Listing
        fields = ['id','product','product_id','seller','price_per_unit','quantity_available','posted_at','expires_at','is_active']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        validated_data['seller'] = user
        return super().create(validated_data)
