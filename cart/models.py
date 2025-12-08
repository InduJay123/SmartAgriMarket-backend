from django.db import models
from crops.models import Crop 

class Cart(models.Model):
    buyer_id = models.IntegerField()  # replace with ForeignKey to User later
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cart'
        unique_together = ('buyer_id', 'crop')
        managed = True

    def __str__(self):
        return f"Buyer {self.buyer_id} - {self.crop.crop_name} x {self.quantity}"
