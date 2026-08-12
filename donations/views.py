from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from causes.models import Cause
from donations.models import Donation
from donations.serializers import CreateDonationSerializer, DonationSerializer
from donations.chapa_client import initialize_transaction, verify_transaction, ChapaError

FRONTEND_BASE_URL = "http://localhost:5173"
BACKEND_BASE_URL = "http://127.0.0.1:8000"


def _mark_paid_if_successful(tx_ref, result):
    if not (
        result.get("status") == "success"
        and result.get("data", {}).get("status") == "success"
    ):
        return Donation.objects.get(tx_ref=tx_ref)

    with transaction.atomic():
        donation = Donation.objects.select_for_update().get(tx_ref=tx_ref)
        if donation.status == "paid":
            return donation

        donation.status = "paid"
        donation.chapa_reference = result["data"].get("reference", "")
        donation.paid_at = timezone.now()
        donation.save()

        Cause.objects.filter(pk=donation.cause_id).update(
            raised_amount=F("raised_amount") + donation.amount
        )

    return donation


class CreateDonationView(generics.CreateAPIView):
    serializer_class = CreateDonationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        donation = serializer.save()

        name_parts = donation.donor_name.split(" ", 1)
        first_name = name_parts[0] if name_parts[0] else "Donor"
        last_name = name_parts[1] if len(name_parts) > 1 else "Tenadam"

        try:
            checkout_url = initialize_transaction(
                amount=donation.amount,
                currency="ETB",
                email=donation.donor_email,
                first_name=first_name,
                last_name=last_name,
                tx_ref=donation.tx_ref,
                callback_url=f"{BACKEND_BASE_URL}/api/donations/webhook/",
                return_url=f"{FRONTEND_BASE_URL}/give-hope/{donation.cause_id}?tx_ref={donation.tx_ref}",
            )
        except ChapaError as exc:
            donation.status = "failed"
            donation.save()
            return Response({"error": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        return Response(
            {"donation_id": donation.id, "tx_ref": donation.tx_ref, "checkout_url": checkout_url},
            status=status.HTTP_201_CREATED,
        )


class ChapaWebhookView(APIView):
    def post(self, request):
        tx_ref = request.data.get("tx_ref")
        if not tx_ref:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        get_object_or_404(Donation, tx_ref=tx_ref)
        result = verify_transaction(tx_ref)
        _mark_paid_if_successful(tx_ref, result)

        return Response(status=status.HTTP_200_OK)


class VerifyDonationView(APIView):
    def get(self, request, tx_ref):
        donation = get_object_or_404(Donation, tx_ref=tx_ref)

        if donation.status != "paid":
            result = verify_transaction(tx_ref)
            donation = _mark_paid_if_successful(tx_ref, result)

        return Response(DonationSerializer(donation).data)
