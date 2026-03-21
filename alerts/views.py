from django.shortcuts import render
from rest_framework.decorators import api_view,  permission_classes
from rest_framework.response import Response
from .models import Alert, UserAlertState
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from django.utils import timezone

from .serializers import UserAlertSerializer
from accounts.models import FarmerDetails, BuyerDetails
from notifications.utils import send_push

#List alerts + unseen count
def get_verified_user_ids():
    farmer_ids = FarmerDetails.objects.filter(is_active=True).values_list("user_id", flat=True)
    buyer_ids = BuyerDetails.objects.filter(is_active=True).values_list("user_id", flat=True)
    return set(farmer_ids) | set(buyer_ids)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_alerts(request):
    # create state if not exists
    state, _ = UserAlertState.objects.get_or_create(user=request.user)

    alerts = Alert.objects.filter(status="SENT").order_by("-id")[:50]
    unseen_count = Alert.objects.filter(status="SENT", id__gt=state.last_seen_alert_id).count()

    data = []
    for a in alerts:
        data.append({
            "id": a.id,
            "title": a.title,
            "message": a.message,
            "category": a.category,
            "level": a.level,
            "alert_type": a.alert_type,
            "crop_name": a.crop_name,
            "created_at": a.created_at,
            "url": a.url,
            "seen": a.id <= state.last_seen_alert_id
        })

    return Response({"unseen_count": unseen_count, "alerts": data})

#Mark all as seen (update last_seen_alert_id)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_all_seen(request):
    state, _ = UserAlertState.objects.get_or_create(user=request.user)
    latest = Alert.objects.filter(status="SENT").order_by("-id").first()
    if latest:
        state.last_seen_alert_id = latest.id
        state.save()
    return Response({"success": True, "last_seen_alert_id": state.last_seen_alert_id})

#Create sudden alert (AI) — send push now
@api_view(["POST"])
@permission_classes([IsAdminUser])  # later you can allow AI service auth instead
def create_sudden_alert(request):
    title = request.data.get("title")
    message = request.data.get("message")
    category = request.data.get("category")  # PRICE/DEMAND/WEATHER
    crop_name = request.data.get("crop_name", None)
    url = request.data.get("url", "/alerts")
    level = request.data.get("level", None) 

    if not title or not message or not category:
        return Response({"error": "title, message, category required"}, status=400)

    if category in ["PRICE", "DEMAND"] and level not in ["HIGH", "LOW"]:
        return Response({"error": "level must be HIGH or LOW for PRICE/DEMAND alerts"}, status=400)

    alert = Alert.objects.create(
        title=title,
        message=message,
        category=category,
        level=level,
        crop_name=crop_name,
        alert_type="SUDDEN",
        status="SENT",
        url=url
    )

    # send to verified + active users
    verified_ids = get_verified_user_ids()
    from django.contrib.auth.models import User
    users = User.objects.filter(id__in=verified_ids, is_active=True, fcmdevice__token__isnull=False).distinct()

    send_push(title, message, users=users, url=url)

    return Response({"success": True, "alert_id": alert.id})

#Create scheduled alert (admin creates now, send later)
@api_view(["POST"])
@permission_classes([IsAdminUser])
def create_scheduled_alert(request):
    title = request.data.get("title")
    message = request.data.get("message")
    category = request.data.get("category")
    scheduled_for = request.data.get("scheduled_for")  # ISO datetime string
    url = request.data.get("url", "/alerts")
    level = request.data.get("level", None)

    if category in ["PRICE", "DEMAND"] and level not in ["HIGH", "LOW"]:
        return Response({"error": "level must be HIGH or LOW for PRICE/DEMAND alerts"}, status=400)
    if not title or not message or not category or not scheduled_for:
        return Response({"error": "title, message, category, scheduled_for required"}, status=400)

    alert = Alert.objects.create(
        title=title,
        message=message,
        category=category,
        level=level,
        alert_type="SCHEDULED",
        status="SCHEDULED",
        scheduled_for=scheduled_for,
        url=url
    )
    return Response({"success": True, "alert_id": alert.id})
