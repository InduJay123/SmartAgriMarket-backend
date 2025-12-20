from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Marketplace,Favourite
from .serializers import MarketplaceSerializer, FavouriteSerializer

@api_view(['GET'])
def get_available_products(request):
    """
    Return all products that are 'Available'
    """
    products = Marketplace.objects.filter(status='Available')
    serializer = MarketplaceSerializer(products, many=True)
    return Response(serializer.data)


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
