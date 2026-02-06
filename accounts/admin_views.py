from asyncio.log import logger
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
        # logger.warning("==== VERIFY HIT ====")
        # logger.warning("content_type=%s", request.content_type)
        # logger.warning("data=%s", request.data)
        # return Response({"ok": True, "data": request.data}, status=200)


        role = request.data.get("role")
        user_id = request.data.get("user_id")
        is_active = request.data.get("is_active")

        if not role or not user_id:
            return Response({"error": "role and user_id are required"}, status=400)

        role_normalized = str(role).strip().lower()

        if role_normalized in ["farmer", "farmers", "f"]:
            model = FarmerDetails
        elif role_normalized in ["buyer", "buyers", "b"]:
            model = BuyerDetails
        else:
            return Response({"error": "role must be Farmer or Buyer"}, status=400)

        profile = model.objects.filter(user_id=user_id).first()
        if not profile:
            return Response({"error": "Profile not found"}, status=404)

        profile.is_active = bool(is_active)
        profile.deactivate_at = timezone.now() if not profile.is_active else None
        profile.save()

       
        return Response({"message": "Updated", "is_active": profile.is_active})


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny

from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

class AdminLoginAPI(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [] 

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Username and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)
        if not user:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Only allow superusers/staff as admin
        if not (user.is_staff or user.is_superuser):
            return Response({"error": "Not an admin account"}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": "Admin"
            }
        }, status=status.HTTP_200_OK)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from .models import FarmerDetails, BuyerDetails
from crops.models import Crop  # your Crop model uses db_table='crops'

class AdminDashboardStatsAPI(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_farmers = FarmerDetails.objects.count()

        verified_farmers = FarmerDetails.objects.filter(is_active=True).count()
        pending_approvals = FarmerDetails.objects.filter(is_active=False).count()

        buyers = BuyerDetails.objects.count()
        crops = Crop.objects.count()

        return Response({
            "verified_farmers": verified_farmers,
            "pending_approvals": pending_approvals,
            "buyers": buyers,
            "crops": crops,
            "total_farmers": total_farmers,
        })
       
