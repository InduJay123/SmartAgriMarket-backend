from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from apps.accounts.models import User
from .serializers import PendingUserSerializer
from .permissions import IsAdminUserOnly

from rest_framework.generics import ListAPIView

from .serializers import FarmerSerializer
from apps.accounts.models import User
from rest_framework.generics import RetrieveAPIView

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .serializers import BuyerSerializer





class PendingUsersView(APIView):
    permission_classes = [IsAdminUserOnly]

    def get(self, request):
        users = User.objects.filter(
            role='FARMER',
            is_verified=False
        )
        serializer = PendingUserSerializer(users, many=True)
        return Response(serializer.data)


class ApproveUserView(APIView):
    permission_classes = [IsAdminUserOnly]

    def patch(self, request, user_id):
        user = get_object_or_404(User, id=user_id, role='FARMER')

        user.is_verified = True
        user.save()

        return Response(
            {"message": "User approved successfully"},
            status=status.HTTP_200_OK
        )

class RejectUserView(APIView):
    permission_classes = [IsAdminUserOnly]

    def patch(self, request, user_id):
        user = get_object_or_404(User, id=user_id, role='FARMER')

        user.delete()

        return Response(
            {"message": "User rejected and removed"},
            status=status.HTTP_200_OK
        )

class FarmerListView(ListAPIView):
    permission_classes = [IsAdminUserOnly]
    serializer_class = FarmerSerializer

    def get_queryset(self):
        queryset = User.objects.filter(role='FARMER')

        status = self.request.query_params.get('status')

        if status == 'verified':
            queryset = queryset.filter(is_verified=True)
        elif status == 'pending':
            queryset = queryset.filter(is_verified=False)
        elif status == 'blocked':
            queryset = queryset.filter(is_active=False)

        return queryset.order_by('-id')

class FarmerDetailView(RetrieveAPIView):
    permission_classes = [IsAdminUserOnly]
    serializer_class = FarmerSerializer
    queryset = User.objects.filter(role='FARMER')

class BlockFarmerView(APIView):
    permission_classes = [IsAdminUserOnly]

    def patch(self, request, farmer_id):
        farmer = get_object_or_404(User, id=farmer_id, role='FARMER')

        farmer.is_active = False
        farmer.save()

        return Response(
            {"message": "Farmer blocked successfully"},
            status=status.HTTP_200_OK
        )    

class UnblockFarmerView(APIView):
    permission_classes = [IsAdminUserOnly]

    def patch(self, request, farmer_id):
        farmer = get_object_or_404(User, id=farmer_id, role='FARMER')

        farmer.is_active = True
        farmer.save()

        return Response(
            {"message": "Farmer unblocked successfully"},
            status=status.HTTP_200_OK
        )

class DeleteFarmerView(APIView):
    permission_classes = [IsAdminUserOnly]

    def delete(self, request, farmer_id):
        farmer = get_object_or_404(User, id=farmer_id, role='FARMER')
        farmer.delete()

        return Response(
            {"message": "Farmer deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )

class BuyerListView(ListAPIView):
    permission_classes = [IsAdminUserOnly]
    serializer_class = BuyerSerializer

    def get_queryset(self):
        queryset = User.objects.filter(role='BUYER')

        status = self.request.query_params.get('status')

        if status == 'verified':
            queryset = queryset.filter(is_verified=True)
        elif status == 'pending':
            queryset = queryset.filter(is_verified=False)
        elif status == 'blocked':
            queryset = queryset.filter(is_active=False)

        return queryset.order_by('-id')

from rest_framework.generics import RetrieveAPIView

class BuyerDetailView(RetrieveAPIView):
    permission_classes = [IsAdminUserOnly]
    serializer_class = BuyerSerializer
    queryset = User.objects.filter(role='BUYER')

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

class BlockBuyerView(APIView):
    permission_classes = [IsAdminUserOnly]

    def patch(self, request, buyer_id):
        buyer = get_object_or_404(User, id=buyer_id, role='BUYER')

        buyer.is_active = False
        buyer.save()

        return Response(
            {"message": "Buyer blocked successfully"},
            status=status.HTTP_200_OK
        )

class UnblockBuyerView(APIView):
    permission_classes = [IsAdminUserOnly]

    def patch(self, request, buyer_id):
        buyer = get_object_or_404(User, id=buyer_id, role='BUYER')

        buyer.is_active = True
        buyer.save()

        return Response(
            {"message": "Buyer unblocked successfully"},
            status=status.HTTP_200_OK
        )

class DeleteBuyerView(APIView):
    permission_classes = [IsAdminUserOnly]

    def delete(self, request, buyer_id):
        buyer = get_object_or_404(User, id=buyer_id, role='BUYER')
        buyer.delete()

        return Response(
            {"message": "Buyer deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )
