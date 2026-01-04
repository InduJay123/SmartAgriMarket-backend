from django.db import models
from django.contrib.auth.models import User

class FarmerDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    fullname = models.CharField(max_length=150,null=True, blank=True)
    farm_name = models.CharField(max_length=100, blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True)

    address = models.TextField(blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    profile_image = models.URLField(blank=True, null=True)

    price_alert = models.BooleanField(default=False)
    buyer_msg = models.BooleanField(default=False)
    harvest_rem = models.BooleanField(default=False)
    market_update = models.BooleanField(default=False)

    reset_token = models.CharField(max_length=100, null=True, blank=True)
    token_created_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.username

class BuyerDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    fullname = models.CharField(max_length=150,null=True, blank=True)
    username = models.CharField(max_length=150, null=True, blank=True) 
    email = models.EmailField(max_length=255, null=True, blank=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)

    company_name = models.CharField(max_length=150, null=True, blank=True)
    company_email = models.EmailField(max_length=255, null=True, blank=True)
    company_phone = models.CharField(max_length=15, null=True, blank=True)

    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    profile_image = models.URLField(blank=True, null=True)

    reset_token = models.CharField(max_length=100, null=True, blank=True)
    token_created_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.user.username