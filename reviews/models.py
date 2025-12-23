from django.db import models

# Create your models here.
from django.db import models
from buyer.models import User
from buyer.models import Marketplace

class Review(models.Model):
    product = models.ForeignKey(Marketplace, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0,null=True, blank=True) 
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "product_reviews"
        ordering = ["-created_at"]
        managed = False

    def __str__(self):
        return f"{self.user.fullname} - {self.product.market_id} ({self.rating}⭐)"
