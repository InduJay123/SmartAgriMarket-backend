from django.urls import path
from .views import SendMessageAPIView, MessageListAPIView, ConversationListAPI, CommunityMessageListAPIView,SendCommunityMessageAPIView, MarkConversationReadAPIView

urlpatterns = [
    path("send-message/", SendMessageAPIView.as_view(), name="send-message"),
    path("messages/<int:user_id>/", MessageListAPIView.as_view(), name="message-list"),
    path("conversations/", ConversationListAPI.as_view()),
    path("messages/<int:user_id>/mark-read/", MarkConversationReadAPIView.as_view()),

    path("community/messages/", CommunityMessageListAPIView.as_view()),
    path("community/send/", SendCommunityMessageAPIView.as_view()),
]