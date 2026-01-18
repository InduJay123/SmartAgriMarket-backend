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
    status = models.CharField(max_length=20, default='PENDING')
    calendar_added = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.crop_name} - {self.category} - {self.alert_type}"