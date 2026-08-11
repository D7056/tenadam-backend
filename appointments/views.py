from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework import generics
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
)
from appointments.models import AvailabilityPeriod, AvailabilityRange, Doctor, Appointment, CustomAvailability





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


class CreateAppointmentView(generics.CreateAPIView):
    serializer_class = CreateAppointmentSerializer
    queryset = Appointment.objects.all()



   
        

