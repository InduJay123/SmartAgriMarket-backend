from rest_framework import serializers
from .models import Order, OrderItem, Transaction
from apps.products.serializers import ListingSerializer
from apps.products.models import Listing

class OrderItemSerializer(serializers.ModelSerializer):
    listing_detail = ListingSerializer(source='listing', read_only=True)
    listing_id = serializers.PrimaryKeyRelatedField(queryset=Listing.objects.all(), source='listing', write_only=True)

    class Meta:
        model = OrderItem
        fields = ['id','listing_detail','listing_id','quantity','unit_price','subtotal']
        read_only_fields = ['unit_price','subtotal']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    buyer = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = ['id','buyer','created_at','status','total_amount','shipping_address','items']
        read_only_fields = ['total_amount','created_at','status','buyer']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        request = self.context.get('request')
        buyer = request.user
        order = Order.objects.create(buyer=buyer, **validated_data)
        total = 0
        for item in items_data:
            listing = item['listing']
            quantity = item['quantity']
            unit_price = listing.price_per_unit
            subtotal = unit_price * quantity
            from .models import OrderItem
            OrderItem.objects.create(order=order, listing=listing, quantity=quantity, unit_price=unit_price, subtotal=subtotal)
            total += subtotal
            # reduce listing quantity_available
            listing.quantity_available = listing.quantity_available - quantity
            listing.save()
        order.total_amount = total
        order.save()
        return order

class TransactionSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())

    class Meta:
        model = Transaction
        fields = ['id','order','provider_txn_id','amount','status','created_at']
        read_only_fields = ['created_at']
