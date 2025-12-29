from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import User,FarmerDetails
from .serializers import UserProfileSerializer, FarmerDetailsSerializer, UserLoginSerializer, UserSignupSerializer
from django.utils import timezone

@api_view(["POST"])
def signup(request):
    serializer = UserSignupSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
def farmer_profile(request, user_id):
    try:
        user = User.objects.get(user_id=user_id)
    except:
        return Response({"error": "Farmer not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "PUT":
        data = request.data

        user.fullname = data.get("fullname", user.fullname)
        user.phone = data.get("phone", user.phone)
        user.region = data.get("region", user.region)
        user.save()

        farmer, created = FarmerDetails.objects.get_or_create(
            user=user,
            defaults={"updated_at": timezone.now()}
            )

        farmer.farm_name = data.get("farm_name", farmer.farm_name)
        farmer.address = data.get("address", farmer.address)
        farmer.city = data.get("city", farmer.city)
        farmer.about = data.get("about", farmer.about)
        farmer.profile_image = data.get("profile_image", farmer.profile_image)
        farmer.price_alert = data.get("price_alert", farmer.price_alert)
        farmer.buyer_msg = data.get("buyer_msg", farmer.buyer_msg)
        farmer.harvest_rem = data.get("harvest_rem", farmer.harvest_rem)
        farmer.market_update = data.get("market_update", farmer.market_update)
        farmer.save()

        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['DELETE'])
def farmer_profile_delete_image(request, user_id):
    try:
        farmer = FarmerDetails.objects.get(user__user=user_id)
    except FarmerDetails.DoesNotExist:
        return Response({"error": "Farmer not found"}, status=status.HTTP_404_NOT_FOUND)

    farmer.profile_image = None  # remove image URL
    farmer.updated_at = timezone.now()
    farmer.save()

    return Response({"message": "Profile image deleted successfully"}, status=status.HTTP_200_OK)