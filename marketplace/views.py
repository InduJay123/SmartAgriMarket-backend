from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Crop, Marketplace, Favourite
from .serializers import CropSerializer, MarketplaceSerializer

@api_view(['GET'])
def get_available_products(request):
    products = Marketplace.objects.filter(status='Available')
    serializer = MarketplaceSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_favourites(request):
    favourites = Favourite.objects.filter(
        user=request.user
    ).select_related('market')

    serializer = MarketplaceSerializer(markets, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favourite(request, market_id):
    try:
        market = Marketplace.objects.get(pk=market_id)
    except Marketplace.DoesNotExist:
        return Response(
            {"error": "Product not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    favourite, created = Favourite.objects.get_or_create(
        user=request.user,
        market=market
    )

    if not created:
        fav.delete()
        return Response({"message": "Removed from favourites"})

    return Response({"message": "Added to favourites"})

class CropViewSet(viewsets.ModelViewSet):
    queryset = Crop.objects.all()
    serializer_class = CropSerializer

    def create(self, request, *args, **kwargs):
        crop_name = request.data.get("crop_name", "").strip()

        if not crop_name:
            return Response({"crop_name": "This field is required."}, status=400)

        crop, created = Crop.objects.get_or_create(
            crop_name__iexact=crop_name,
            defaults={
                "crop_name": crop_name,
                "description": request.data.get("description", ""),
                "image": request.data.get("image"),
                "category": request.data.get("category"),
            }
        )

        serializer = self.get_serializer(crop)
        return Response(serializer.data, status=201 if created else 200)


class MarketplaceViewSet(viewsets.ModelViewSet):
    queryset = Marketplace.objects.select_related('crop').all()
    serializer_class = MarketplaceSerializer

    def get_queryset(self):
        return Marketplace.objects.select_related('crop').filter(
            farmer_id=self.request.user.id
        )

    def perform_create(self, serializer):
        # If crop ID is provided, use it directly
        crop_id = self.request.data.get("crop")
        if crop_id:
            from .models import Crop
            try:
                crop = Crop.objects.get(crop_id=crop_id)
            except Crop.DoesNotExist:
                raise ValueError("Invalid crop ID.")
        else:
            # Otherwise, create/get crop by name
            crop_name = self.request.data.get("crop_name") or self.request.data.get("customCrop")
            if not crop_name:
                raise ValueError("Crop name is required.")
            crop, _ = Crop.objects.get_or_create(
                crop_name__iexact=crop_name.strip(),
                defaults={
                    "crop_name": crop_name.strip(),
                    "description": self.request.data.get("description", ""),
                    "image": self.request.data.get("image"),
                    "category": self.request.data.get("category", "General")
                }
            )

        serializer.save(farmer_id=self.request.user.id, crop=crop)

    def create(self, request, *args, **kwargs):
        print("Marketplace CREATE data:", request.data)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        print("Marketplace UPDATE data:", request.data)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        print("Marketplace PATCH data:", request.data)
        return super().partial_update(request, *args, **kwargs)
