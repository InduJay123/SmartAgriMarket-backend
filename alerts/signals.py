# alerts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Alert
from notifications.utils import send_push
from django.contrib.auth.models import User

@receiver(post_save, sender=Alert)
def alert_created_notify(sender, instance, created, **kwargs):
    if created:
        title = f"New {instance.category} Alert!"
        body = instance.message
        # Send to all users (or filter users if needed)
        users = User.objects.filter(fcmdevice__isnull=False,is_active=True)  # Filter farmers if you have a Farmer role
        print("Sending alert to users:", users)
        send_push(title, body, users)