from django.urls import path
from .views import get_user_alerts, mark_alert_sent

urlpatterns = [
    path('user-alerts/', get_user_alerts, name="get_user_alerts"),
    path('user-alerts/<int:alert_id>/sent/', mark_alert_sent, name="mark_user_alert_sent"),
]
