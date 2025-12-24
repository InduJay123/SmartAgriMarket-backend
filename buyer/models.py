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
    farming_season = models.CharField(max_length=255)
    additional_details = models.CharField(max_length=255)
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
    fullname = models.CharField(max_length=100)
    username = models.CharField(max_length=255)
    email = models.CharField(max_length=100, db_index=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone = models.IntegerField()  # longblob
    region = models.CharField(max_length=100, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'users'
        managed = False  # because table is already created manually

    def __str__(self):
        return self.fullname

class BuyerDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="buyer_details")
    company_name = models.CharField(max_length=150, null=True, blank=True)
    company_email = models.CharField(max_length=150, null=True, blank=True)
    company_phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    profile_image = models.CharField(max_length=255, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'buyer_details'
        managed = False  # Change to True if you want Django to create this table

    def __str__(self):
        return f"{self.user.username} Details"

class Favourite(models.Model):
    user_id = models.IntegerField(default=1)  # hardcode user_id=1 for now
    market = models.ForeignKey('Marketplace', on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'favourites'
        unique_together = ('user_id', 'market')

    def __str__(self):
        return f"User {self.user_id} favourite: {self.market.crop.crop_name}"
