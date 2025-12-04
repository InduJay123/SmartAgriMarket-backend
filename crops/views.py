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

        crop_name = request.data.get("crop_name", "").strip()

        if not crop_name:
            return Response({"crop_name": "This field is required."}, status=400)

        # Check if the crop already exists
        crop, created = Crop.objects.get_or_create(
            crop_name__iexact=crop_name,  # case-insensitive check
            defaults={
                "crop_name": crop_name,
                "description": request.data.get("description", ""),
                "image": request.data.get("image", None),
                "category": request.data.get("category", None),
            }
        )

        serializer = self.get_serializer(crop)
        if created:
            return Response(serializer.data, status=201)  # New crop created
        else:
            return Response(serializer.data, status=200)  # Existing crop returned

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