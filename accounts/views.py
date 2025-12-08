from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import User
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # /api/users/pending/
    @action(detail=False, methods=["get"])
    def pending(self, request):
        users = User.objects.filter(is_verified=False, is_rejected=False)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    # /api/users/counts/
    @action(detail=False, methods=["get"])
    def counts(self, request):
        return Response({
            "verified_farmers": User.objects.filter(user_type="farmer", is_verified=True).count(),
            "pending_approvals": User.objects.filter(is_verified=False, is_rejected=False).count(),
            "buyers": User.objects.filter(user_type="buyer").count(),
            "crops": User.objects.filter(user_type="farmer").count(),
        })

    # /api/users/<id>/approve/
    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        user = self.get_object()
        user.is_verified = True
        user.is_rejected = False
        user.save()
        return Response({"message": "User approved"})

    # /api/users/<id>/reject/
    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        user = self.get_object()
        user.is_verified = False
        user.is_rejected = True
        user.save()
        return Response({"message": "User rejected"})
