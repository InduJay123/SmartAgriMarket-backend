from django.shortcuts import render
from rest_framework.decorators import api_view,  permission_classes
from rest_framework.response import Response
from .models import Alert, UserAlert
from .serializers import UserAlertSerializer
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_alerts(request):
    user = request.user
    alerts = UserAlert.objects.filter(user = user, status='PENDING')
    serializer = UserAlertSerializer(alerts, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_alert_sent(request, alert_id):
    user = request.user
    try:
        user_alert = UserAlert.objects.get(user=user,id=alert_id)
        user_alert.status = "SENT"
        user_alert.seen_at = timezone.now()
        user_alert.save()
        return Response({"message": "Alert marked as sent for this user"})
    except UserAlert.DoesNotExist:
        return Response({"error": "Alert not found for this uuser"}, status=404)