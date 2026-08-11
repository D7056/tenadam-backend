from django.db import models
from accounts.models import User


class Cause(models.Model):
    CATEGORY_CHOICES = [
        ("individual", "Individual"),
        ("organization", "Organization"),
    ]

    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="causes")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    name = models.CharField(max_length=100)
    tagline = models.CharField(max_length=150)
    description = models.TextField()
    location = models.CharField(max_length=100)
    goal_amount = models.DecimalField(max_digits=10, decimal_places=2)
    raised_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({'approved' if self.approved else 'pending'})"


class CauseDocument(models.Model):
    cause = models.ForeignKey(Cause, on_delete=models.CASCADE, related_name="documents")
    file = models.FileField(upload_to="cause_documents/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
