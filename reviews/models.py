from django.db import models
from django.contrib.auth.models import User
from marketplace.models import Marketplace


class Review(models.Model):
    # db_constraint=False: Marketplace table is managed=False (not Django-owned);
    # the ORM relation still works but no DB-level FK is enforced.
    product = models.ForeignKey(
        Marketplace,
        on_delete=models.CASCADE,
        related_name='reviews',
        db_constraint=False,
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0,null=True, blank=True) 
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reviews"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.fullname} - {self.product.market_id} ({self.rating}⭐)"