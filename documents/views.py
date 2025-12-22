from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import PriceList
from .serializers import PriceListSerializer
from rest_framework import status
from buyer.models import User

# Create your views here.
@api_view(['GET'])
def get_priceList(request):
    documents = PriceList.objects.all().order_by('-upload_date')
    serializer =  PriceListSerializer(documents, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def upload_price_list(request):
    admin = User.objects.first()

    price_list = PriceList.objects.create(
        filename=request.data.get('filename'),
        file_url=request.data.get('file_url'),
        uploaded_by=admin
    )

    return Response(
        {"message": "Mock price list uploaded"},
        status=status.HTTP_201_CREATED
    )