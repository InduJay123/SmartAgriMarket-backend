from django.urls import path
from .admin_views import (
    PriceTrendsReport,
    FarmersActivityReport,
    MarketTransactionsReport
)

urlpatterns = [
    path('admin/reports/price-trends/', PriceTrendsReport.as_view()),
    path('admin/reports/farmers-activity/', FarmersActivityReport.as_view()),
    path('admin/reports/market-transactions/', MarketTransactionsReport.as_view()),
]
