from django.db import models
from accounts.models import ProviderProfile
import appointments.choices


# Create your models here.
class Doctor(models.Model):
    provider = models.OneToOneField(ProviderProfile, on_delete=models.CASCADE, related_name="doctor")
    doctor_type=models.CharField(max_length=50, choices=appointments.choices.DOCTOR_TYPE_CHOICES)
    duration_minutes = models.PositiveIntegerField(default=30)
    fee_enabled = models.BooleanField(default=False)
    fee_amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)


class AvailabilityPeriod(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="availability_periods")
    active_from = models.DateField()
    active_until = models.DateField(null=True, blank=True)


class AvailabilityRange(models.Model):
    class Weekday(models.IntegerChoices):
        MONDAY = 0, "Monday"
        TUESDAY = 1, "Tuesday"
        WEDNESDAY = 2, "Wednesday"
        THURSDAY = 3, "Thursday"
        FRIDAY = 4, "Friday"
        SATURDAY = 5, "Saturday"
        SUNDAY = 6, "Sunday"

    period = models.ForeignKey(AvailabilityPeriod, on_delete=models.CASCADE, related_name="ranges")
    day_of_week = models.IntegerField(choices=Weekday.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()


class CustomAvailability(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="custom_times")
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    note = models.CharField(max_length=255, blank=True)


class Appointment(models.Model):
    STATUS_CHOICES = [
        ("upcoming", "Upcoming"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("not_required", "Not Required"),
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    ]

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="appointments")
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    reason = models.CharField(max_length=100)
    reason_note = models.CharField(max_length=255, blank=True)
    patient_name = models.CharField(max_length=100)
    patient_phone = models.CharField(max_length=20)
    patient_email = models.EmailField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="upcoming")
    created_at = models.DateTimeField(auto_now_add=True)

    fee_amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default="not_required"
    )
    tx_ref = models.CharField(max_length=100, unique=True, null=True, blank=True)
    chapa_reference = models.CharField(max_length=100, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["doctor", "date", "start_time"],
                condition=~models.Q(status="cancelled"),
                name="unique_doctor_date_start_time_unless_cancelled",
            )
        ]

