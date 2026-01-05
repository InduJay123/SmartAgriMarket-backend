from rest_framework.views import APIView
from django.db.models import Q, Max
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Chat
from .serializers import ChatSerializer

class SendMessageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        receiver_id = request.data.get("receiver_id")
        content = request.data.get("content")

        if not receiver_id or not content:
            return Response({"error": "receiver_id and content are required"}, status=400)

        chat = Chat.objects.create(
            sender=request.user,
            receiver_id=receiver_id,
            content=content
        )
        return Response(ChatSerializer(chat).data, status=201)


class MessageListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        # Fetch all messages between logged-in user and user_id
        chat = Chat.objects.filter(
            sender_id__in=[request.user.id, user_id],
            receiver_id__in=[request.user.id, user_id]
        ).order_by("timestamp")

        return Response(ChatSerializer(chat, many=True).data)

class ConversationListAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Get all messages involving logged user
        messages = Chat.objects.filter(
            Q(sender=user) | Q(receiver=user)
        )

        conversations = {}

        for msg in messages:
            other_user = msg.receiver if msg.sender == user else msg.sender

            profile_image = None
            try:
                if hasattr(other_user, "farmerdetails"):
                    profile_image = other_user.farmerdetails.profile_image
                elif hasattr(other_user, "buyerdetails"):
                    profile_image = other_user.buyerdetails.profile_image
            except:
                profile_image = None

            # keep latest message only
            if (
                other_user.id not in conversations
                or msg.timestamp > conversations[other_user.id]["timestamp"]
            ):
                conversations[other_user.id] = {
                    "user_id": other_user.id,
                    "username": other_user.username,
                    "last_message": msg.content,
                    "timestamp": msg.timestamp,
                    "profile_image": profile_image
                }

        return Response(conversations.values())