from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .services import ReportsService


class PriceTrendsReport(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        data = ReportsService.price_trends()
        return Response(data)


class FarmersActivityReport(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        data = ReportsService.farmers_activity()
        return Response(data)


class MarketTransactionsReport(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        data = ReportsService.market_transactions()
        return Response(data)
