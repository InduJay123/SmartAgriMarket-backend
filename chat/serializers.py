from rest_framework import serializers
from .models import Chat, CommunityMessage

class ChatSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    receiver_username = serializers.CharField(source='receiver.username', read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'sender', 'receiver', 'sender_username',
         'receiver_username', 'content', 'timestamp', 'is_read']

class CommunityMessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source="sender.username", read_only=True)

    class Meta:
        model = CommunityMessage
        fields = ["id", "sender", "sender_username", "content", "timestamp"]