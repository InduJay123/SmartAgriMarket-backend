# notifications/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import FCMDevice

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def register_token(request):
    token = request.data.get("token")
    FCMDevice.objects.update_or_create(
        user=request.user,
        defaults={"token": token}
    )
    return Response({"success": True})