from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)

class UserManager(BaseUserManager): # controls how user are created
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Emai is Required")
        
        email = self.normalize_email(email) # convert email to stamdard format
        user = self.model(email=email, **extra_fields) #create user object
        user.set_password(password) #converts pwd into a hashed
        user.save(using=self._db) # save user into the db
        return user #return the created user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True) #can access admin panel
        extra_fields.setdefault("is_superuser", True) #full permisssions
        extra_fields.setdefault("role", "Admin")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    fullname = models.CharField(max_length=100)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    ROLE_CHOICES = (
        ("Farmer", "Farmer"),
        ("Buyer", "Buyer"),
        ("Admin", "Admin"),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone = models.IntegerField(null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)

    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "fullname"]

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.email

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True

class FarmerDetails(models.Model):
    id = models.AutoField(primary_key=True)

    user = models.OneToOneField(
        User,
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
