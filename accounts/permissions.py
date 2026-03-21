from rest_framework.permissions import BasePermission
from .models import FarmerDetails, BuyerDetails

class IsActiveFarmer(BasePermission):
    message = "Farmer not activate by admin yet."

    def has_permission(self, request, view):
        # Farmers are active immediately after signup, no admin approval needed
        return True

class IsActiveBuyer(BasePermission):
    message = "Buyer not activate by admin yet."

    def has_permission(self, request, view):
        # Buyers are active immediately after signup, no admin approval needed
        return True

class IsActiveUser(BasePermission):
    message = "Account not activate by admin yet."

    def has_permission(self, request, view):
        # Users are active immediately after signup, no admin approval needed
        return True