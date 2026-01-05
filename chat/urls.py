from django.urls import path
from .views import SendMessageAPIView, MessageListAPIView, ConversationListAPI

urlpatterns = [
    path("send-message/", SendMessageAPIView.as_view(), name="send-message"),
    path("messages/<int:user_id>/", MessageListAPIView.as_view(), name="message-list"),
    path("conversations/", ConversationListAPI.as_view()),
]