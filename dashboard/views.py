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
        pending_approvals = FarmerDetails.objects.filter(
            is_active=False,
            user__is_active=True,
        ).count()
        buyers = BuyerDetails.objects.count()

        crops = Crop.objects.count()

        return Response({
            "verified_farmers": verified_farmers,
            "pending_approvals": pending_approvals,
            "buyers": buyers,
            "crops": crops,
            "total_farmers": total_farmers,
        })
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.db.models import Avg

from marketplace.models import Marketplace


class AdminPriceChartAPI(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            data = (
                Marketplace.objects
                .select_related("crop")
                .values("crop__crop_name")
                .annotate(avg_price=Avg("price"))
            )

            labels = []
            values = []

            for item in data:
                labels.append(item["crop__crop_name"])
                values.append(float(item["avg_price"]))

            return Response({
                "labels": labels,
                "values": values
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)