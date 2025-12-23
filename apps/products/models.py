from django.db import models
from django.conf import settings

class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100, blank=True)
    default_unit = models.CharField(max_length=20, default='kg')
    image = models.ImageField(upload_to='products/', null=True, blank=True)

    def __str__(self):
        return self.name

class Listing(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='listings')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='listings')
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_available = models.DecimalField(max_digits=12, decimal_places=3)
    posted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-posted_at']

    def __str__(self):
        return f"{self.product.name} by {self.seller.email}"
    


class Price(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
   # region = models.CharField(max_length=100)
    #created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.price} on {self.date}"


class Crop(models.Model):
    CATEGORY_CHOICES = (
        ('Vegetable', 'Vegetable'),
        ('Grain', 'Grain'),
        ('Fruit', 'Fruit'),
    )

    SEASON_CHOICES = (
        ('Yala', 'Yala'),
        ('Maha', 'Maha'),
        ('All season', 'All season'),
    )

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    season = models.CharField(max_length=20, choices=SEASON_CHOICES)
    avg_price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20, default='kg')

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
