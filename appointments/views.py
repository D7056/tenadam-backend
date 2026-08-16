import uuid
from django.db import transaction
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from datetime import date as date_cls

from appointments.serializers import (
    AvailabilitySerializer,
    FeesandDurationsSerializer,
    BookedSlotSerializer,
    CreateAppointmentSerializer,
    CustomAvailabilitySerializer,
    AppointmentDetailSerializer,
)
from appointments.models import AvailabilityPeriod, AvailabilityRange, Doctor, Appointment, CustomAvailability
from donations.chapa_client import initialize_transaction, verify_transaction, ChapaError

FRONTEND_BASE_URL = "http://localhost:5173"
BACKEND_BASE_URL = "http://127.0.0.1:8000"





class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        provider = getattr(request.user, "provider_profile", None)
        doctor = getattr(provider, "doctor", None)
        if doctor is None:
            return False
        request.doctor = doctor  
        return True

class CreateAvailabilityView(generics.CreateAPIView):
    permission_classes=[IsAuthenticated, IsDoctor]
    serializer_class=AvailabilitySerializer

    

    def perform_create(self, serializer):
        serializer.save(doctor=self.request.doctor)
class MyAvailabilityView(generics.ListAPIView):
    serializer_class=AvailabilitySerializer
    permission_classes=[IsAuthenticated, IsDoctor]

    def get_queryset(self):
        doctor=self.request.doctor
        return AvailabilityPeriod.objects.filter(doctor=doctor).prefetch_related("ranges")
class UpdateDurationandFeesView(generics.UpdateAPIView):
    serializer_class=FeesandDurationsSerializer
    permission_classes=[IsAuthenticated, IsDoctor]

    def get_object(self):
        return self.request.doctor


class CreateCustomAvailabilityView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsDoctor]
    serializer_class = CustomAvailabilitySerializer

    def perform_create(self, serializer):
        serializer.save(doctor=self.request.doctor)


class MyCustomAvailabilityView(generics.ListAPIView):
    serializer_class = CustomAvailabilitySerializer
    permission_classes = [IsAuthenticated, IsDoctor]

    def get_queryset(self):
        return CustomAvailability.objects.filter(doctor=self.request.doctor)


class DeleteCustomAvailabilityView(generics.DestroyAPIView):
    serializer_class = CustomAvailabilitySerializer
    permission_classes = [IsAuthenticated, IsDoctor]

    def get_queryset(self):
        return CustomAvailability.objects.filter(doctor=self.request.doctor)


class DoctorAvailabilityView(APIView):
    """Public: lets a patient see a specific doctor's posted availability."""

    def get(self, request, doctor_id):
        doctor = get_object_or_404(Doctor, id=doctor_id)
        periods = AvailabilityPeriod.objects.filter(doctor=doctor).prefetch_related("ranges")
        custom_times = CustomAvailability.objects.filter(
            doctor=doctor, date__gte=date_cls.today()
        )
        return Response({
            "duration_minutes": doctor.duration_minutes,
            "periods": AvailabilitySerializer(periods, many=True).data,
            "custom_times": CustomAvailabilitySerializer(custom_times, many=True).data,
        })


class DoctorBookedSlotsView(APIView):
    """Public: lets a patient see which slots are already taken, to grey them out."""

    def get(self, request, doctor_id):
        qs = Appointment.objects.filter(doctor_id=doctor_id).exclude(status="cancelled")

        date_from = request.query_params.get("from")
        date_to = request.query_params.get("to")
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)

        serializer = BookedSlotSerializer(qs, many=True)
        return Response(serializer.data)


def _mark_appointment_paid(tx_ref, result):
    if not (
        result.get("status") == "success"
        and result.get("data", {}).get("status") == "success"
    ):
        return Appointment.objects.get(tx_ref=tx_ref)

    with transaction.atomic():
        appointment = Appointment.objects.select_for_update().get(tx_ref=tx_ref)
        if appointment.payment_status == "paid":
            return appointment

        appointment.payment_status = "paid"
        appointment.chapa_reference = result["data"].get("reference", "")
        appointment.paid_at = timezone.now()
        appointment.save()

    return appointment


class CreateAppointmentView(generics.CreateAPIView):
    serializer_class = CreateAppointmentSerializer
    queryset = Appointment.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = serializer.save()

        if appointment.payment_status != "pending":
            return Response(
                {
                    "appointment_id": appointment.id,
                    "payment_required": False,
                    "appointment": AppointmentDetailSerializer(appointment).data,
                },
                status=status.HTTP_201_CREATED,
            )

        tx_ref = f"tenadam-appt-{uuid.uuid4().hex[:16]}"
        name_parts = appointment.patient_name.split(" ", 1)
        first_name = name_parts[0] if name_parts[0] else "Patient"
        last_name = name_parts[1] if len(name_parts) > 1 else "Tenadam"

        try:
            checkout_url = initialize_transaction(
                amount=appointment.fee_amount,
                currency="ETB",
                email=appointment.patient_email,
                first_name=first_name,
                last_name=last_name,
                tx_ref=tx_ref,
                callback_url=f"{BACKEND_BASE_URL}/api/appointments/payments/webhook/",
                return_url=f"{FRONTEND_BASE_URL}/book/{appointment.doctor_id}?tx_ref={tx_ref}",
            )
        except ChapaError as exc:
            appointment.status = "cancelled"
            appointment.payment_status = "failed"
            appointment.save()
            return Response({"error": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        appointment.tx_ref = tx_ref
        appointment.save()

        return Response(
            {
                "appointment_id": appointment.id,
                "payment_required": True,
                "tx_ref": tx_ref,
                "checkout_url": checkout_url,
            },
            status=status.HTTP_201_CREATED,
        )


class AppointmentPaymentWebhookView(APIView):
    def post(self, request):
        tx_ref = request.data.get("tx_ref")
        if not tx_ref:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        get_object_or_404(Appointment, tx_ref=tx_ref)
        result = verify_transaction(tx_ref)
        _mark_appointment_paid(tx_ref, result)

        return Response(status=status.HTTP_200_OK)


class VerifyAppointmentPaymentView(APIView):
    def get(self, request, tx_ref):
        appointment = get_object_or_404(Appointment, tx_ref=tx_ref)

        if appointment.payment_status != "paid":
            result = verify_transaction(tx_ref)
            appointment = _mark_appointment_paid(tx_ref, result)

        return Response(AppointmentDetailSerializer(appointment).data)

