from django.urls import path
from .views import list_alerts, mark_all_seen, create_sudden_alert, create_scheduled_alert

urlpatterns = [
    path("alerts/", list_alerts),
    path("mark-seen/", mark_all_seen),
    path("sudden/", create_sudden_alert),
    path("scheduled/", create_scheduled_alert),
]