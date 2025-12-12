from rest_framework import viewsets, permissions, filters
from .models import Product, Listing
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
