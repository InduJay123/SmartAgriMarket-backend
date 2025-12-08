from django.db import models

class User(models.Model):

    USER_TYPES = (
        ("farmer", "Farmer"),
        ("buyer", "Buyer"),
        ("admin", "Admin"),
    )

    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    district = models.CharField(max_length=50)
    user_type = models.CharField(max_length=10, choices=USER_TYPES)

    applied_date = models.DateField(auto_now_add=True)

    is_verified = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name} ({self.user_type})"
