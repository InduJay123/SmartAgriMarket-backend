from firebase_admin import messaging
from .models import FCMDevice
from django.contrib.auth.models import User

def send_push(title: str, body: str, users=None):
    """
    Send FCM push notifications.
    - title: Notification title
    - body: Notification body
    - users: Optional list/queryset of User objects to target specific users
    """
    if users:
        tokens = FCMDevice.objects.filter(user__in=users).values_list("token", flat=True)
    else:
        tokens = FCMDevice.objects.values_list("token", flat=True)

    for token in tokens:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=token,
        )

        try:
            messaging.send(message)
        except Exception as e:
            print(f"Error sending to token {token}: {e}")