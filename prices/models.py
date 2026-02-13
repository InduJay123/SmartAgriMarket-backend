from django.db import models
from django.conf import settings

class PriceUpload(models.Model):
    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("PROCESSED", "Processed"),
        ("FAILED", "Failed"),
    )

    file = models.FileField(upload_to="price_uploads/")
    original_name = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    processed_rows = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.original_name} ({self.status})"


class CropPrice(models.Model):
    crop_name = models.CharField(max_length=100)
    date = models.DateField()
    market = models.CharField(max_length=120, blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    unit = models.CharField(max_length=50, blank=True, null=True)

    upload = models.ForeignKey(PriceUpload, on_delete=models.CASCADE, related_name="prices")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.crop_name} - {self.date} - {self.price}"
