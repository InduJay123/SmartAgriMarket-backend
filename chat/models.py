from django.db import models
from django.contrib.auth.models import User

class Chat(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        db_table = 'chat'

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username} at {self.timestamp}"