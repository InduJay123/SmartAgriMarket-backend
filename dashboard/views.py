from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from accounts.models import FarmerDetails, BuyerDetails  # adjust if your model paths differ
from django.contrib.auth import get_user_model
from crops.models import Crop  # adjust if your Crop model name differs

User = get_user_model()

class AdminDashboardStatsAPI(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        verified_farmers = User.objects.filter(role="FARMER", is_verified=True).count()
        pending_approvals = User.objects.filter(role="FARMER", is_verified=False).count()
        buyers = User.objects.filter(role="BUYER").count()

        crops = Crop.objects.count()

        return Response({
            "verified_farmers": verified_farmers,
            "pending_approvals": pending_approvals,
            "buyers": buyers,
            "crops": crops,
        })
