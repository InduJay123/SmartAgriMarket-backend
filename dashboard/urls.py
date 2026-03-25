from django.urls import path
from .views import AdminDashboardStatsAPI, AdminPriceChartAPI

urlpatterns = [
    path("admin/dashboard-stats/", AdminDashboardStatsAPI.as_view()),
    path("admin/price-chart/", AdminPriceChartAPI.as_view()),
]