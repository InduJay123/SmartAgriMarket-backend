from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from .models import PriceList
from .serializers import PriceListSerializer
from rest_framework import status
from accounts.models import User

# Create your views here.
@api_view(['GET'])
def get_priceList(request):
    documents = PriceList.objects.all().order_by('-upload_date')
    serializer =  PriceListSerializer(documents, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def upload_price_list(request):
    filename = request.data.get("filename")
    file_url = request.data.get("file_url")

    if not filename or not file_url:
        return Response(
            {"error": "filename and file_url are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    admin_user = User.objects.filter(email=request.user.email).first()
    if not admin_user:
        return Response({"error": "Admin user not found in accounts User table"}, status=400)
        
    print("auth request.user id:", request.user.id, "email:", request.user.email)
    print("accounts admin_user:", admin_user.pk if admin_user else None)

    PriceList.objects.create(
        filename=filename,
        file_url=file_url,
        uploaded_by=request.user
    )

    return Response(
        {"message": "Price list uploaded successfully"},
        status=status.HTTP_201_CREATED
    )