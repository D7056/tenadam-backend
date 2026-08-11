import uuid
from django.db import models
from causes.models import Cause


def generate_tx_ref():
    return f"tenadam-{uuid.uuid4().hex[:16]}"


class Donation(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    ]

    cause = models.ForeignKey(Cause, on_delete=models.CASCADE, related_name="donations")
    donor_name = models.CharField(max_length=100)
    donor_phone = models.CharField(max_length=20)
    donor_email = models.EmailField(blank=True)
    note = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    tx_ref = models.CharField(max_length=100, unique=True, default=generate_tx_ref)
    chapa_reference = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.donor_name} - {self.amount} ({self.status})"
