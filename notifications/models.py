from django.db import models
from django.contrib.auth.models import User

class FCMDevice(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.TextField()

    def __str__(self):
        return f"{self.user.username} - FCM"