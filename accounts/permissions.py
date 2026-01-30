from rest_framework.permissions import BasePermission
from .models import FarmerDetails, BuyerDetails

class IsActiveFarmer(BasePermission):
    message = "Farmer not activate by admin yet."

    def has_permission(self, request, view):
        return FarmerDetails.objects.filter(user=request.user, is_active=True).exists()

class IsActiveBuyer(BasePermission):
    message = "Buyer not activate by admin yet."

    def has_permission(self, request, view):
        return BuyerDetails.objects.filter(user=request.user, is_active=True).exists()

class IsActiveUser(BasePermission):
    message = "Account not activate by admin yet."

    def has_permission(self, request, view):
        return (
            FarmerDetails.objects.filter(user=request.user, is_active=True).exists()
            or BuyerDetails.objects.filter(user=request.user, is_active=True).exists()
        )