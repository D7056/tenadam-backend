from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("User must have a phone number.")
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    ROLE_CHOICES=[("customer", "Customer"),
                   ('provider', 'Provider')]

    phone_number=models.CharField(max_length=20, unique=True)
    first_name=models.CharField(max_length=30)
    last_name=models.CharField(max_length=30)
    roles=models.CharField(max_length=30, choices=ROLE_CHOICES, default="customer")
    email=models.EmailField(blank=True)
    address=models.CharField(max_length=255, null=True, default=None)
    profile_completed=models.BooleanField(default=False)
    is_active=models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)


    objects=UserManager()
    
    USERNAME_FIELD="phone_number"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone_number})"

class ProviderProfile(models.Model):
    SERVICE_TYPE_CHOICES = [
        ("medicine_dealer", "Medicine Dealer"),
        ("delivery_man", "Delivery Man"),
        ("doctor", "Doctor"),
    ]

    user= models.OneToOneField(User, on_delete=models.CASCADE, related_name="provider_profile")

    service_type=models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES)
    
    employer=models.CharField(max_length=50, default="self-employed")
    approved= models.BooleanField(default=False)


    def __str__(self):
        return f"{self.user} - {self.get_service_type_display()}"

