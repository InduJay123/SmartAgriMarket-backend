from rest_framework import viewsets
from .models import Crop, Marketplace
from .serializers import CropSerializer, MarketplaceSerializer
from rest_framework.response import Response
from rest_framework import status

class CropViewSet(viewsets.ModelViewSet):
    queryset = Crop.objects.all()
    serializer_class = CropSerializer

    def create(self, request, *args, **kwargs):
        print("REQUEST DATA --->", request.data)  # DEBUG
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            print("ERRORS --->", serializer.errors)  # REAL REASON FOR 400
            return Response(serializer.errors, status=400)

        self.perform_create(serializer)
        return Response(serializer.data, status=201)

class MarketplaceViewSet(viewsets.ModelViewSet):
    queryset = Marketplace.objects.all()
    serializer_class = MarketplaceSerializer

    def get_queryset(self):
        return Marketplace.objects.select_related('crop').filter(farmer_id = 1)
    
    def update(self, request, *args, **kwargs):
        print("UPDATE REQUEST DATA:", request.data)  # debug
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        print("PATCH REQUEST DATA:", request.data)  # debug
        return super().partial_update(request, *args, **kwargs)