from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from accounts.models import FarmerDetails, BuyerDetails
from crops.models import Crop

class AdminDashboardStatsAPI(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_farmers = FarmerDetails.objects.count()
        verified_farmers = FarmerDetails.objects.filter(is_active=True).count()
        pending_approvals = FarmerDetails.objects.filter(is_active=False).count()
        buyers = BuyerDetails.objects.count()

        crops = Crop.objects.count()

        return Response({
            "verified_farmers": verified_farmers,
            "pending_approvals": pending_approvals,
            "buyers": buyers,
            "crops": crops,
            "total_farmers": total_farmers,
        })
