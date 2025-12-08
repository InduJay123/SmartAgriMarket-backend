from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Marketplace
from .serializers import MarketplaceSerializer

@api_view(['GET'])
def get_available_products(request):
    """
    Return all products that are 'Available'
    """
    products = Marketplace.objects.filter(status='Available')
    serializer = MarketplaceSerializer(products, many=True)
    return Response(serializer.data)
