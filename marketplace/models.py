from django.db import models
from django.contrib.auth.models import User

class Crop(models.Model):
    crop_id = models.AutoField(primary_key=True)
    crop_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'crops'
        managed = False

    def __str__(self):
        return self.crop_name


class Marketplace(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Sold', 'Sold'),
        ('Pending', 'Pending'),
    ]

    market_id = models.AutoField(primary_key=True)
    farmer_id = models.IntegerField()
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name="markets")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20)
    predicted_date = models.DateField()
    quantity = models.IntegerField()
    farming_method = models.CharField(max_length=100, default='Unknown')
    farming_season = models.CharField(max_length=100)
    region = models.CharField(max_length=255)
    district = models.CharField(max_length=255)
    image = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')

    class Meta:
        db_table = 'market'
        managed = False

    def __str__(self):
        return f"{self.crop.crop_name} - {self.status}"


class Favourite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favourites"
    )
    market = models.ForeignKey(
        Marketplace,
        on_delete=models.CASCADE,
        related_name="favourited_by",
        to_field='market_id'
    )

    class Meta:
        db_table = 'marketplace_favourites'
        unique_together = ('user', 'market')
        managed = False

    def __str__(self):
        return f"{self.user.username} ❤️ {self.market.market_id}"