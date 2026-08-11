from django.contrib import admin
from .models import Donation


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ["donor_name", "cause", "amount", "status", "tx_ref", "created_at"]
    list_filter = ["status"]
    search_fields = ["donor_name", "donor_phone", "tx_ref"]
