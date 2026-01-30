# alerts/admin.py
from django.contrib import admin
from .models import Alert

class AlertAdmin(admin.ModelAdmin):
    list_display = ('crop_name', 'category', 'alert_type', 'message', 'created_at')

    def save_model(self, request, obj, form, change):
        # This is called whenever you create/edit Alert from admin
        super().save_model(request, obj, form, change)

        if not change:  # only new alerts
            from notifications.utils import send_push
            title = f"New {obj.category} Alert!"
            body = obj.message
            users_with_tokens = obj.useralert_set.all()  # or User.objects.filter(fcmdevice__isnull=False)
            send_push(title, body, users_with_tokens)

admin.site.register(Alert, AlertAdmin)