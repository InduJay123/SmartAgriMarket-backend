from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Marketplace,Favourite,User,BuyerDetails
from .serializers import MarketplaceSerializer, FavouriteSerializer, BuyerProfileSerializer

#products
@api_view(['GET'])
def get_available_products(request):
    """
    Return all products that are 'Available'
    """
    products = Marketplace.objects.filter(status='Available')
    serializer = MarketplaceSerializer(products, many=True)
    return Response(serializer.data)



#favourites products
@api_view(['GET'])
def get_favourites(request):
    user_id = request.query_params.get('user_id')

    if not user_id:
        return Response([], status=200)

    favourites = Favourite.objects.filter(user_id=user_id)

    # get related marketplace products
    markets = [f.market for f in favourites]

    serializer = MarketplaceSerializer(markets, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def toggle_favourite(request):
    user_id = request.data.get('user_id')
    market_id = request.data.get('product_id')

    if not user_id or not market_id:
        return Response(
            {"error": "user_id and product_id are required"},
            status=400
        )

    try:
        market = Marketplace.objects.get(market_id=market_id)
    except Marketplace.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)

    fav, created = Favourite.objects.get_or_create(
        user_id=user_id,
        market=market
    )

    if not created:
        fav.delete()
        return Response({"message": "Removed from favourites"})

    return Response({"message": "Added to favourites"})



#buyer profile
Example_data = {
    "company_name": "Example Market",
    "company_email": "example@market.com",
    "company_phone": "+94 71 2345678",
    "address": "No 12, Example Street",
    "city": "Galle",
    "postal_code": "80000",
    "profile_image": "/media/default-avatar.png"
}

@api_view(['GET'])
def get_buyer_profile(request, user_id):
    try:
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    try:
        profile = user.buyer_details
        serializer = BuyerProfileSerializer(profile)
        return Response(serializer.data)
    except BuyerDetails.DoesNotExist:
        data = Example_data.copy()
        data.update({
            "user_id": user.user_id,
            "fullname": user.fullname,
            "username": user.username,
            "email": user.email,
            "phone": str(user.phone),
        })

        for key, value in Example_data.items():
            if not data.get(key):
                data[key] = value
        return Response(data)

@api_view(['PUT'])
def update_buyer_profile(request, user_id):
    try:
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    # -------------------
    # UPDATE USER TABLE
    # -------------------
    user.fullname = request.data.get("fullname", user.fullname)
    user.username = request.data.get("username", user.username)
    user.email = request.data.get("email", user.email)
    user.phone = request.data.get("phone", user.phone)
    user.save()

    # -------------------
    # UPDATE BUYER DETAILS
    # -------------------
    profile, created = BuyerDetails.objects.get_or_create(user=user)

    serializer = BuyerProfileSerializer(
        profile,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                "message": "Profile updated successfully",
                "user_id": user.user_id
            },
            status=200
        )

    return Response(serializer.errors, status=400)

@api_view(['DELETE'])
def delete_buyer_profile_image(request, user_id):
    try:
        user = User.objects.get(user_id=user_id)
        profile = BuyerDetails.objects.get(user=user)
    except (User.DoesNotExist, BuyerDetails.DoesNotExist):
        return Response({"error": "profile not found"}, status=404)

    profile.profile_image = None
    profile.save()

    return Response(
        {"message": "Profile image removed succesfully"},
        status=200
    )