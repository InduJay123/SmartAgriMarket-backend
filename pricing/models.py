from django.db import models
from mcrops.models import Crop

class PriceRecord(models.Model):
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        return f"{self.crop.name} - {self.price}"
