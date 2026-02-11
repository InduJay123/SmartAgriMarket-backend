from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings

class Notification(models.Model):
    notify_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column="user_id")
    related_crop_id = models.IntegerField(null=True, blank=True)
    type = models.CharField(max_length=50)
    title = models.CharField(max_length=150)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default="ACTIVE")

    class Meta:
        db_table = "notifications"
