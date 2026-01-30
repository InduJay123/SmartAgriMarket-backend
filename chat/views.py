from rest_framework.views import APIView
from django.db.models import Q, Max
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Chat, CommunityMessage
from .serializers import ChatSerializer, CommunityMessageSerializer
from accounts.permissions import IsActiveUser

def is_farmer(user):
    return hasattr(user, "farmerdetails")

class SendMessageAPIView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

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
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get(self, request, user_id):
        chat = Chat.objects.filter(
            sender_id__in=[request.user.id, user_id],
            receiver_id__in=[request.user.id, user_id]
        ).order_by("timestamp")

        return Response(ChatSerializer(chat, many=True).data)

class ConversationListAPI(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get(self, request):
        user = request.user

        # Get all messages involving logged user
        messages = Chat.objects.filter(
            Q(sender=user) | Q(receiver=user)
        )

        conversations = {}

        for msg in messages:
            other_user = msg.receiver if msg.sender == user else msg.sender

            unread_count = Chat.objects.filter(
                sender=other_user,
                receiver=user,
                is_read=False
            ).count()
            
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
                    "profile_image": profile_image,
                    "unread_count": unread_count,  
                }

        return Response(conversations.values())

class MarkConversationReadAPIView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    def post(self, request, user_id):
        Chat.objects.filter(
            sender_id=user_id,
            receiver=request.user,
            is_read=False
        ).update(is_read=True)

        return Response({"ok": True})

class CommunityMessageListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get(self, request):
        if not is_farmer(request.user):
            return Response({"error": "Only farmers can access community chat"}, status=403)

        msgs = CommunityMessage.objects.select_related("sender").order_by("timestamp")[:300]
        return Response(CommunityMessageSerializer(msgs, many=True).data)

class SendCommunityMessageAPIView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    def post(self, request):
        if not is_farmer(request.user):
            return Response({"error": "Only farmers can send community messages"}, status=403)

        content = request.data.get("content")
        if not content:
            return Response({"error": "content is required"}, status=400)

        msg = CommunityMessage.objects.create(sender=request.user, content=content)
        return Response(CommunityMessageSerializer(msg).data, status=201)