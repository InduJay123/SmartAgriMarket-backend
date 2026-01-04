from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import status
from .serializers import SignupSerializer
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from .models import FarmerDetails, BuyerDetails
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny

class SignupAPI(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Account created successfully"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginAPI(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        role = request.data.get('role') 

        if not email or not password or not role:
            return Response(
                {"error": "Email, password and role are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Find user by email safely
        user_obj = User.objects.filter(email=email).first()
        if not user_obj:
            return Response({"error": "Invalid email"}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate using username (Django way)
        user = authenticate(
            username=user_obj.username,
            password=password
        )

        if not user:
            return Response({"error": "Incorrect password"}, status=status.HTTP_400_BAD_REQUEST)

        if role == "Farmer" and not hasattr(user, 'farmerdetails'):
            return Response({"error": "User is not a farmer"}, status=status.HTTP_400_BAD_REQUEST)
        if role == "Buyer" and not hasattr(user, 'buyerdetails'):
            return Response({"error": "User is not a buyer"}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": role
            }
        })

class FarmerProfileAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            farmer = user.farmerdetails
            data = {
                "id": user.id,
                "first_name":  user.username,
                "email": user.email,
                "phone": farmer.contact_number,
                "farmer_details": {
                    "fullname": farmer.fullname,
                    "farm_name": farmer.farm_name,
                    "address": getattr(farmer, "address", ""),
                    "region": farmer.region,
                    "about": getattr(farmer, "about", ""),
                    "profile_image": getattr(farmer, "profile_image", ""),
                    "price_alert": getattr(farmer, "price_alert", False),
                    "buyer_msg": getattr(farmer, "buyer_msg", False),
                    "harvest_rem": getattr(farmer, "harvest_rem", False),
                    "market_update": getattr(farmer, "market_update", False),
                }
            }
            
            return Response(data, status=status.HTTP_200_OK)
        except FarmerDetails.DoesNotExist:
            return Response({"error": "Farmer profile not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        user = request.user
        try:
            farmer = user.farmerdetails
            data = request.data

            farmer.fullname = data.get("fullname", farmer.fullname)
            farmer.contact_number = data.get("phone", farmer.contact_number)
            farmer.farm_name = data.get("farm_name", farmer.farm_name)
            farmer.address = data.get("address", getattr(farmer, "address", ""))
            farmer.region = data.get("region", farmer.region)
            farmer.about = data.get("about", getattr(farmer, "about", ""))
            farmer.profile_image = data.get("profile_image", getattr(farmer, "profile_image", ""))
            farmer.price_alert = data.get("price_alert", getattr(farmer, "price_alert", False))
            farmer.buyer_msg = data.get("buyer_msg", getattr(farmer, "buyer_msg", False))
            farmer.harvest_rem = data.get("harvest_rem", getattr(farmer, "harvest_rem", False))
            farmer.market_update = data.get("market_update", getattr(farmer, "market_update", False))

            farmer.save()
            return Response({"message": "Profile updated successfully"}, status=status.HTTP_200_OK)

        except FarmerDetails.DoesNotExist:
            return Response({"error": "Farmer profile not found"}, status=status.HTTP_404_NOT_FOUND)

class DeleteProfileImageAPI(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            farmer = request.user.farmerdetails
            farmer.profile_image = ""
            farmer.save()
            return Response({"message": "Profile image deleted"})
        except:
            return Response({"error": "Farmer profile not found"}, status=404)

class BuyerProfileAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            buyer = user.buyerdetails
            data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "phone": buyer.contact_number,
                "buyer_details": {
                    "fullname": buyer.fullname,
                    "company_name": buyer.company_name,
                    "company_email": buyer.company_email,
                    "company_phone": buyer.company_phone,
                    "profile_image": getattr(buyer, "profile_image", ""),
                    "street_address": getattr(buyer, "street_address", ""),
                    "city": getattr(buyer, "city", ""),
                }
            }
            return Response(data, status=status.HTTP_200_OK)
        except BuyerDetails.DoesNotExist:
            return Response({"error": "Buyer profile not found"}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request):
        user = request.user
        try:
            buyer = user.buyerdetails
            data = request.data

            buyer.fullname = data.get("fullname", buyer.fullname)
            buyer.contact_number = data.get("phone", buyer.contact_number)
            buyer.username = data.get("username", buyer.username)
            buyer.email = data.get("email", buyer.email)

            buyer.company_name = data.get("market_name", buyer.company_name)
            buyer.company_email = data.get("company_email", buyer.company_email)
            buyer.company_phone = data.get("company_phone", buyer.company_phone)

            buyer.street_address = data.get("street_address", getattr(buyer, "street_address", ""))
            buyer.city = data.get("city", getattr(buyer, "city", ""))
            buyer.profile_image = data.get("profile_image", getattr(buyer, "profile_image", ""))
            
            buyer.save()
            return Response({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "phone": buyer.contact_number,
                "buyer_details": {
                    "fullname": buyer.fullname,
                    "company_name": buyer.company_name,
                    "company_email": buyer.company_email,
                    "company_phone": buyer.company_phone,
                    "profile_image": buyer.profile_image,
                    "street_address": buyer.street_address,
                    "city": buyer.city,
                }
            })

        except BuyerDetails.DoesNotExist:
            return Response({"error": "Buyer profile not found"}, status=status.HTTP_404_NOT_FOUND)


class DeleteBuyerProfileImageAPI(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            buyer = request.user.buyerdetails
            if hasattr(buyer, "profile_image"):
                buyer.profile_image = ""
                buyer.save()
                return Response({"message": "Buyer profile image deleted"})
            else:
                return Response({"error": "No profile image found"}, status=404)
        except BuyerDetails.DoesNotExist:
            return Response({"error": "Buyer profile not found"}, status=404)
