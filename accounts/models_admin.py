# accounts/models_admin.py (or put in accounts/models.py)
from django.db import models
from django.contrib.auth.models import User

class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="admin_profile")

    phone = models.CharField(max_length=20, blank=True, null=True)

    email_notifications = models.BooleanField(default=True)
    price_alert_notifications = models.BooleanField(default=True)
    system_update_notifications = models.BooleanField(default=False)

    def __str__(self):
        return f"AdminProfile({self.user.username})"
