from django.db import models

class Users(models.Model):
    user_id = models.AutoField(primary_key=True)
    fullname = models.CharField(max_length=100)
    username = models.CharField(max_length=255)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=10)  # Farmer | Buyer | Admin
    phone = models.IntegerField(null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField()

    class Meta:
        db_table = "users"
        managed = False

class FarmerDetails(models.Model):
    id = models.AutoField(primary_key=True)

    user = models.OneToOneField(
        Users,
        on_delete=models.CASCADE,
        db_column="user_id",
        related_name="farmer_details"
    )

    profile_image = models.CharField(max_length=255, null=True, blank=True)
    farm_name = models.CharField(max_length=150, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    price_alert = models.BooleanField(default=False)
    buyer_msg = models.BooleanField(default=False)
    harvest_rem = models.BooleanField(default=False)
    market_update = models.BooleanField(default=False)
    about = models.TextField(null=True, blank=True)  
    updated_at = models.DateTimeField()

    class Meta:
        db_table = "farmer_details"
        managed = False
