from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Cart
from crops.models import Crop
from .serializers import CartSerializer

class CartViewSet(viewsets.ViewSet):
    def list(self, request, buyer_id=None):
        """Get All cart items for a buyer"""
        cart_items = Cart.objects.filter(buyer_id=buyer_id)
        serializer = CartSerializer(cart_items, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add(self,request):
        """Add item to cart"""
        buyer_id = request.data.get('buyer_id')
        crop_id = request.data.get('crop_id')
        quantity = request.data.get('quantity',1)

        try:
            crop = Crop.onjects.get(crop_id = crop_id)
        except Crop.DoesNotExist:
            return Response({'error': 'Crop not found'}, status=status.HTTP_404_NOT_FOUND)

        cart_item, created = Cart.objects.get_or_create(buyer_id=buyer_id, crop=crop)
        