from django.db import models
from accounts.models import User

class Crop(models.Model):
    name = models.CharField(max_length=100)
    farmer = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.FloatField()
    unit = models.CharField(max_length=10)
    district = models.CharField(max_length=50)

    def __str__(self):
        return self.name