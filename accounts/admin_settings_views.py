from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate

from .models_admin import AdminProfile
from .serializers_admin_settings import AdminSettingsSerializer

class AdminSettingsAPI(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        u = request.user
        return Response({
            "username": u.username,
            "email": u.email,
        })

    def put(self, request):
        u = request.user

        username = request.data.get("username", u.username)
        email = request.data.get("email", u.email)

        u.username = username
        u.email = email
        u.save()

        return Response({"message": "Settings updated"})

class AdminChangePasswordAPI(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not old_password or not new_password:
            return Response({"error": "old_password and new_password are required"}, status=400)

        # verify old password
        if not request.user.check_password(old_password):
            return Response({"error": "Old password is incorrect"}, status=400)

        # validate new password using Django validators
        try:
            validate_password(new_password, user=request.user)
        except ValidationError as e:
            return Response({"error": e.messages[0]}, status=400)

        request.user.set_password(new_password)
        request.user.save()

        return Response({"message": "Password updated"}, status=200)
