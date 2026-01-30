from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Alert, UserAlertState
from notifications.utils import send_push
from django.contrib.auth.models import User

@receiver(post_save, sender=Alert)
def alert_created_notify(sender, instance, created, **kwargs):
    if not created:
        return

    users = User.objects.filter(is_active=True)

    send_push(
        title=f"New {instance.category} Alert!",
        body=instance.message,
        users=users
    )