from django.db import models
from django.contrib.auth.models import User

# Crop model
class Crop(models.Model):
    crop_id = models.AutoField(primary_key=True)
    crop_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.CharField(max_length=255, blank=True, null=True)  # Can store file path or URL
    category = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.crop_name
    
    class Meta:
        db_table = 'crops'
        managed = False

# Marketplace model
class Marketplace(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Sold', 'Sold'),
        ('Pending', 'Pending'),
    ]

    market_id = models.AutoField(primary_key=True)
    farmer_id = models.IntegerField()
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20)
    predicted_date = models.DateField()
    quantity = models.IntegerField()
    farming_method = models.CharField(max_length=255)
    farming_season = models.CharField(max_length=255)
    additional_details = models.CharField(max_length=255,blank=True,null=True)
    region = models.CharField(max_length =255)
    district = models.CharField(max_length=255)
    image = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.crop.crop_name} - ({self.status})"

    class Meta:
        db_table = 'market'
        managed = False