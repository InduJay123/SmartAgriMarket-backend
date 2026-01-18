from django.urls import path
from .views import get_alerts, mark_alert_sent

urlpatterns = [
    path('alerts/', get_alerts),
    path("alerts/<int:alert_id>/sent/", mark_alert_sent),
]