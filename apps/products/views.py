from rest_framework import viewsets, permissions, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Product, Listing, Price
from .serializers import ProductSerializer, ListingSerializer
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.generics import ListCreateAPIView

from rest_framework.filters import SearchFilter
from .models import Crop
from .serializers import CropSerializer
from apps.adminpanel.permissions import IsAdminUserOnly

from rest_framework.generics import RetrieveUpdateAPIView

from rest_framework.views import APIView

from rest_framework import status
from django.shortcuts import get_object_or_404


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


class AdminCropListCreateView(ListCreateAPIView):
    permission_classes = [IsAdminUserOnly]
    serializer_class = CropSerializer
    queryset = Crop.objects.filter(is_active=True)

    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['name']
    filterset_fields = ['category', 'season']
    ordering_fields = ['avg_price', 'created_at']

class AdminCropUpdateView(RetrieveUpdateAPIView):
    permission_classes = [IsAdminUserOnly]
    serializer_class = CropSerializer
    queryset = Crop.objects.all()

class AdminCropDeleteView(APIView):
    permission_classes = [IsAdminUserOnly]

    def delete(self, request, crop_id):
        crop = get_object_or_404(Crop, id=crop_id)
        crop.is_active = False
        crop.save()

        return Response(
            {"message": "Crop deleted successfully"},
            status=status.HTTP_200_OK
        )