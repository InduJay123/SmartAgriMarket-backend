from django.urls import path
from .views import AdminDashboardStatsAPI

urlpatterns = [
    path("admin/dashboard-stats/", AdminDashboardStatsAPI.as_view()),
]
