from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from .models import FarmerDetails, BuyerDetails
from .serializers_admin import FarmerAdminSerializer, BuyerAdminSerializer
from crops.models import Crop


def _to_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "y", "on"}:
            return True
        if normalized in {"false", "0", "no", "n", "off", ""}:
            return False
    if value in (0, 1):
        return bool(value)
    return None


class AdminLoginAPI(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Username and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(username=username, password=password)
        if not user:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

        if not (user.is_staff or user.is_superuser):
            return Response({"error": "Not an admin account"}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": "Admin",
                },
            },
            status=status.HTTP_200_OK,
        )


class AdminFarmersListAPI(APIView):
    """
    GET /api/auth/admin/farmers/
    Optional query param: ?status=pending|active|rejected  (default: all)

    pending  — registered, awaiting review  (profile.is_active=False, user.is_active=True)
    active   — approved by admin            (profile.is_active=True)
    rejected — rejected by admin            (profile.is_active=False, user.is_active=False)
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        status_param = request.query_params.get("status", "all")
        qs = FarmerDetails.objects.select_related("user").order_by("-id")

        if status_param == "pending":
            qs = qs.filter(is_active=False, user__is_active=True)
        elif status_param == "active":
            qs = qs.filter(is_active=True)
        elif status_param == "rejected":
            qs = qs.filter(is_active=False, user__is_active=False)

        serializer = FarmerAdminSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminBuyersListAPI(APIView):
    """
    GET /api/auth/admin/buyers/
    Optional query param: ?status=pending|active|rejected  (default: all)
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        status_param = request.query_params.get("status", "all")
        qs = BuyerDetails.objects.select_related("user").order_by("-id")

        if status_param == "pending":
            qs = qs.filter(is_active=False, user__is_active=True)
        elif status_param == "active":
            qs = qs.filter(is_active=True)
        elif status_param == "rejected":
            qs = qs.filter(is_active=False, user__is_active=False)

        serializer = BuyerAdminSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminPendingUsersAPI(APIView):
    """
    GET /api/auth/admin/pending-users/
    Returns all farmers and buyers who registered but have not yet been approved or rejected.
    pending = profile.is_active=False AND user.is_active=True
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        pending_farmers = FarmerDetails.objects.filter(
            is_active=False, user__is_active=True
        ).select_related("user").order_by("-id")

        pending_buyers = BuyerDetails.objects.filter(
            is_active=False, user__is_active=True
        ).select_related("user").order_by("-id")

        return Response(
            {
                "farmers": FarmerAdminSerializer(pending_farmers, many=True).data,
                "buyers": BuyerAdminSerializer(pending_buyers, many=True).data,
            },
            status=status.HTTP_200_OK,
        )


class AdminVerifyUserAPI(APIView):
    """
    PATCH /api/auth/admin/verify/
    Body: { "role": "Farmer"|"Buyer", "user_id": <int>, "is_active": true|false }

    Approve (is_active=true):  profile.is_active=True,  user.is_active=True
    Reject  (is_active=false): profile.is_active=False, user.is_active=False
    This lets the pending list distinguish between "not yet reviewed" and "rejected".
    """
    permission_classes = [IsAdminUser]

    def patch(self, request):
        role = request.data.get("role")
        user_id = request.data.get("user_id")
        is_active = request.data.get("is_active")

        if not role or user_id is None:
            return Response({"error": "role and user_id are required"}, status=400)

        role_normalized = str(role).strip().lower()

        if role_normalized in ["farmer", "farmers", "f"]:
            model = FarmerDetails
        elif role_normalized in ["buyer", "buyers", "b"]:
            model = BuyerDetails
        else:
            return Response({"error": "role must be Farmer or Buyer"}, status=400)

        profile = model.objects.filter(user_id=user_id).select_related("user").first()
        if not profile:
            return Response({"error": "Profile not found"}, status=404)

        approved = _to_bool(is_active)
        if approved is None:
            return Response({"error": "is_active must be true or false"}, status=400)

        # Update profile status
        profile.is_active = approved
        profile.deactivate_at = None if approved else timezone.now()
        profile.save()

        # Sync Django User.is_active so the pending filter works correctly:
        #   approved  → user can log in (user.is_active=True)
        #   rejected  → user cannot log in (user.is_active=False)
        profile.user.is_active = approved
        profile.user.save(update_fields=["is_active"])

        return Response({"message": "Updated", "is_active": profile.is_active})


class AdminDashboardStatsAPI(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_farmers = FarmerDetails.objects.count()
        verified_farmers = FarmerDetails.objects.filter(is_active=True).count()
        # pending = registered but not yet reviewed (excludes rejected users)
        pending_approvals = FarmerDetails.objects.filter(
            is_active=False, user__is_active=True
        ).count()
        buyers = BuyerDetails.objects.count()
        crops = Crop.objects.count()

        return Response(
            {
                "verified_farmers": verified_farmers,
                "pending_approvals": pending_approvals,
                "buyers": buyers,
                "crops": crops,
                "total_farmers": total_farmers,
            }
        )


class AdminUserDetailAPI(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, user_id):
        # Frontend currently sends list item `id` from admin lists.
        # Accept both user_id and profile PK to keep the existing button behavior working.
        farmer = FarmerDetails.objects.filter(user_id=user_id).select_related("user").first()
        if not farmer:
            farmer = FarmerDetails.objects.filter(pk=user_id).select_related("user").first()
        if farmer:
            return Response({
                "id": farmer.user_id,
                "profile_id": farmer.id,
                "role": "Farmer",
                "email": farmer.user.email,
                "username": farmer.user.username,
                "fullname": farmer.fullname,
                "contact_number": farmer.contact_number,
                "region": farmer.region,
                "farm_name": farmer.farm_name,
                "address": farmer.address,
                "about": farmer.about,
                "profile_image": farmer.profile_image,
                "is_active": farmer.is_active,
            })

        buyer = BuyerDetails.objects.filter(user_id=user_id).select_related("user").first()
        if not buyer:
            buyer = BuyerDetails.objects.filter(pk=user_id).select_related("user").first()
        if buyer:
            return Response({
                "id": buyer.user_id,
                "profile_id": buyer.id,
                "role": "Buyer",
                "email": buyer.user.email,
                "username": buyer.user.username,
                "fullname": buyer.fullname,
                "contact_number": buyer.contact_number,
                "company_name": buyer.company_name,
                "company_email": buyer.company_email,
                "company_phone": buyer.company_phone,
                "address": buyer.address,
                "city": buyer.city,
                "profile_image": buyer.profile_image,
                "is_active": buyer.is_active,
            })

        return Response({"error": "Profile not found"}, status=404)

