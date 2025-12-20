from django.db import models

# Crop model
class Crop(models.Model):
    crop_id = models.AutoField(primary_key=True)
    crop_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.CharField(max_length=255, blank=True, null=True)  # URL or file path
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
    region = models.CharField(max_length=255)
    district = models.CharField(max_length=255)
    image = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.crop.crop_name} - ({self.status})"

    class Meta:
        db_table = 'market'
        managed = False



class User(models.Model):
    ROLE_CHOICES = [
        ('Farmer', 'Farmer'),
        ('Buyer', 'Buyer'),
        ('Admin', 'Admin'),
    ]

    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100, db_index=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone = models.IntegerField()  # longblob
    region = models.CharField(max_length=100, null=True, blank=True)
    profile_image = models.CharField(max_length=255, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'users'
        managed = False  # because table is already created manually

    def __str__(self):
        return self.name
