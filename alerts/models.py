from django.contrib.auth.models import User
from django.db import models

class Alert(models.Model):
    CATEGORY_CHOICES = [
        ('PRICE', 'Price'),
        ('DEMAND', 'Demand'),
        ('WEATHER', 'Weather'),
    ]

    crop_name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    alert_type = models.CharField(max_length=20)  # SUDDEN or SCHEDULED
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class UserAlert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default="PENDING")  # PENDING or SENT
    seen_at = models.DateTimeField(null=True, blank=True)