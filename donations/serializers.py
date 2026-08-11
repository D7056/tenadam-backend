from rest_framework import serializers
from donations.models import Donation


class CreateDonationSerializer(serializers.ModelSerializer):
    donor_email = serializers.EmailField(required=True)

    class Meta:
        model = Donation
        fields = ["id", "cause", "donor_name", "donor_phone", "donor_email", "note", "amount"]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value


class DonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = [
            "id", "cause", "donor_name", "amount", "status",
            "tx_ref", "created_at", "paid_at",
        ]
