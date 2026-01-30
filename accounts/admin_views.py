from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from django.utils import timezone

from .models import FarmerDetails, BuyerDetails
from .serializers_admin import FarmerAdminSerializer, BuyerAdminSerializer


class AdminFarmersListAPI(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        farmers = FarmerDetails.objects.select_related("user").all().order_by("-id")
        serializer = FarmerAdminSerializer(farmers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminBuyersListAPI(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        buyers = BuyerDetails.objects.select_related("user").all().order_by("-id")
        serializer = BuyerAdminSerializer(buyers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AdminVerifyUserAPI(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request):
        role = request.data.get("role")  
        user_id = request.data.get("user_id")
        is_active = request.data.get("is_active")  

        if role not in ["Farmer", "Buyer"]:
            return Response({"error": "role must be Farmer or Buyer"}, status=400)

        model = FarmerDetails if role == "Farmer" else BuyerDetails
        profile = model.objects.filter(user_id=user_id).first()
        if not profile:
            return Response({"error": "Profile not found"}, status=404)

        profile.is_active = bool(is_active)
        profile.deactivate_at = timezone.now() if not profile.is_active else None
        profile.save()

        return Response({"message": "Updated", "is_active": profile.is_active})