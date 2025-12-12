from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from .models import Order, Transaction
from .serializers import OrderSerializer, TransactionSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related('items').all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(buyer=user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status in ['completed','cancelled']:
            return Response({'detail':'Cannot cancel'}, status=status.HTTP_400_BAD_REQUEST)
        order.status = 'cancelled'
        order.save()
        return Response({'status':'cancelled'})

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.select_related('order').all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        txn = ser.save()
        return Response(self.get_serializer(txn).data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def payment_webhook(request):
    data = request.data
    provider_txn_id = data.get('provider_txn_id')
    order_id = data.get('order_id')
    status_str = data.get('status')
    from .models import Order, Transaction
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'detail':'order not found'}, status=status.HTTP_404_NOT_FOUND)

    txn, created = Transaction.objects.get_or_create(order=order, defaults={'provider_txn_id':provider_txn_id,'amount':data.get('amount',0),'status':status_str})
    if not created:
        txn.provider_txn_id = provider_txn_id
        txn.status = status_str
        txn.save()

    if status_str in ['success','completed','paid']:
        order.status = 'confirmed'
        order.save()
    elif status_str in ['failed','cancelled']:
        order.status = 'cancelled'
        order.save()

    return Response({'ok':True})
