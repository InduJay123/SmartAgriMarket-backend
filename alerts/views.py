from django.shortcuts import render
from rest_framework.decorators import api_view,  permission_classes
from rest_framework.response import Response
from .models import Alert
from .serializers import AlertSerializer
from rest_framework.permissions import IsAuthenticated

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_alerts(request):
    alerts = Alert.objects.filter(status='PENDING')
    serializer = AlertSerializer(alerts, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_alert_sent(request, alert_id):
    try:
        alert = Alert.objects.get(id=alert_id)
        alert.status = "SENT"
        alert.save()
        return Response({"message": "Alert marked as sent"})
    except Alert.DoesNotExist:
        return Response({"error": "Alert not found"}, status=404)