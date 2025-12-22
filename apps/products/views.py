from rest_framework import viewsets, permissions, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Product, Listing, Price
from .serializers import ProductSerializer, ListingSerializer
from django_filters.rest_framework import DjangoFilterBackend

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name','category']
    ordering_fields = ['name']

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.select_related('product','seller').all()
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product__id','seller__id','is_active']
    search_fields = ['product__name']
    ordering_fields = ['price_per_unit','posted_at']

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

@api_view(['GET'])
def tomato_price_chart(request):
    try:
        tomato = Product.objects.get(name__iexact='tomato')
        prices = (
            Price.objects
            .filter(product=tomato)
            .order_by('-date')[:6]
        )

        prices = reversed(prices)  # correct order

        return Response({
            "labels": [p.date.strftime('%b') for p in prices],
            "prices": [p.price for p in prices],
        })

    except Product.DoesNotExist:
        return Response({"error": "Tomato product not found"}, status=404)
