from firebase_admin import messaging
from .firebase import init_firebase
from .models import FCMDevice
from django.contrib.auth.models import User

def send_push(title: str, body: str, users=None, url: str | None = None):
    """
    Send FCM push notifications.
    - title: Notification title
    - body: Notification body
    - users: Optional list/queryset of User objects to target specific users
    """
    init_firebase()
    
    qs = FCMDevice.objects.all()
    if users is not None:
        qs = qs.filter(user__in=users)

    tokens = qs.values_list("token", flat=True)

    for token in tokens:
        if not token:
            continue

        data = {}
        if url:
            data["url"] = url 
            
        msg = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            token=token,
            data=data
        )
        try:
            messaging.send(msg)
        except Exception as e:
            print("FCM error:", e)