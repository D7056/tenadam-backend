from django.db import models
from accounts.models import User, ProviderProfile

# Create your models here.

class Order(models.Model):
    STATUS_CHOICES=[
        ("pending", "Pending"),
        ('picked_up','Picked Up'),
        ('complete',"Complete")

    ]

    customer=models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    provider=models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name='orders')

    status=models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")

    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer} -> {self.provider}"



class Item(models.Model):
    dealer=models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    dosages = models.JSONField(max_length=50, blank=True)
    img_url = models.TextField(blank=True)

class OrderItem(models.Model):
    order= models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, blank=True, related_name="order_items")
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    dosage = models.CharField(max_length=50, blank=True)


    def __str__(self):
        return f"{self.title} x{self.quantity}"



    




