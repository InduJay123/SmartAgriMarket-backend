from django.db import models
from django.contrib.auth.models import User

class Alert(models.Model):
    CATEGORY_CHOICES = [
        ("PRICE", "Price"),
        ("DEMAND", "Demand"),
        ("WEATHER", "Weather"),
    ]
    TYPE_CHOICES = [
        ("SUDDEN", "Sudden"),
        ("SCHEDULED", "Scheduled"),
    ]
    STATUS_CHOICES = [
        ("SCHEDULED", "Scheduled"),
        ("SENT", "Sent"),
    ]

    LEVEL_CHOICES = [
        ("LOW", "Low"),
        ("HIGH", "High"),
        ("NORMAL", "Normal"), 
    ]

    title = models.CharField(max_length=150,default="System Alert")
    message = models.TextField()
    crop_name = models.CharField(max_length=100, blank=True, null=True)

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    alert_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="SENT")

    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default="NORMAL")
    scheduled_for = models.DateTimeField(null=True, blank=True)  # only for scheduled
    created_at = models.DateTimeField(auto_now_add=True)

    # optional: where notification click should go
    url = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.category})"


class UserAlertState(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    last_seen_alert_id = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} last_seen={self.last_seen_alert_id}"