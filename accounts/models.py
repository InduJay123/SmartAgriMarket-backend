from django.db import models
from django.contrib.auth.models import User

class FarmerDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=150,null=True, blank=True)
    farm_name = models.CharField(max_length=100, blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.user.username

class BuyerDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=150,null=True, blank=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.user.username