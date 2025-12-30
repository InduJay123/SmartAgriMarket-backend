from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import status
from .serializers import SignupSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

class SignupAPI(APIView):
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

        profile_data = {}
        if role == "Farmer":
            if not hasattr(user, 'farmerdetails'):
                return Response({"error": "User is not a farmer"}, status=400)
            profile = user.farmerdetails
            profile_data = {
                "fullname": profile.fullname,
                "farm_name": profile.farm_name,
                "contact_number": profile.contact_number,
            }

        elif role == "Buyer":
            if not hasattr(user, 'buyerdetails'):
                return Response({"error": "User is not a buyer"}, status=400)
            profile = user.buyerdetails
            profile_data = {
                "fullname": profile.fullname,
                "contact_number": profile.contact_number,
                "city": profile.city,
                "address": profile.address,
            }

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
