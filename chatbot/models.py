from django.db import models
from django.utils import timezone

class ChatSession(models.Model):
    """Stores chatbot conversation sessions"""
    session_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    context = models.JSONField(default=dict, blank=True)  # Store conversation context

    def __str__(self):
        return f"Session {self.session_id}"

    class Meta:
        ordering = ['-updated_at']


class ChatMessage(models.Model):
    """Stores individual chat messages"""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('bot', 'Bot'),
    ]

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    message = models.TextField()
    intent = models.CharField(max_length=100, blank=True, null=True)
    confidence = models.FloatField(default=0.0)
    metadata = models.JSONField(default=dict, blank=True)  # Store intent scores, entities, etc.
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role}: {self.message[:50]}..."

    class Meta:
        ordering = ['created_at']
