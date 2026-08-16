from rest_framework import serializers
from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import Q
from appointments.models import AvailabilityRange, AvailabilityPeriod, Doctor, Appointment, CustomAvailability



class AvailabilityRangeSerializer(serializers.ModelSerializer):

    class Meta:
        model=AvailabilityRange
        fields=["id","day_of_week", "start_time", "end_time"]
class AvailabilitySerializer(serializers.ModelSerializer):
    ranges=AvailabilityRangeSerializer(many=True)
    class Meta:
        model=AvailabilityPeriod
        fields=["id","ranges","active_from","active_until",]
    def create(self, validated_data):
        ranges=validated_data.pop("ranges")
        
        with transaction.atomic():
            availabilityperiod=AvailabilityPeriod.objects.create(**validated_data)
            for i in range(0,len(ranges)):
                x=ranges[i]
                AvailabilityRange.objects.create(
                    period=availabilityperiod,
                    **x
                )
        return availabilityperiod
class FeesandDurationsSerializer(serializers.ModelSerializer):

    class Meta:
        model=Doctor
        fields=["id",'duration_minutes', "fee_amount","fee_enabled"]


class CustomAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomAvailability
        fields = ["id", "date", "start_time", "end_time", "note"]

    def validate(self, data):
        if data["start_time"] >= data["end_time"]:
            raise serializers.ValidationError("start_time must be before end_time.")
        return data


class BookedSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ["date", "start_time"]


class CreateAppointmentSerializer(serializers.ModelSerializer):
    patient_email = serializers.EmailField(required=False, allow_blank=True)

    class Meta:
        model = Appointment
        fields = [
            "id", "doctor", "date", "start_time", "end_time",
            "reason", "reason_note", "patient_name", "patient_phone",
            "patient_email", "status", "payment_status", "fee_amount",
        ]
        read_only_fields = ["status", "payment_status", "fee_amount"]

    def validate(self, data):
        doctor = data["doctor"]
        date = data["date"]
        start_time = data["start_time"]
        end_time = data["end_time"]

        if start_time >= end_time:
            raise serializers.ValidationError("start_time must be before end_time.")

        if doctor.fee_enabled and not data.get("patient_email", "").strip():
            raise serializers.ValidationError(
                "This doctor requires a booking fee, so an email is needed to process payment."
            )

        weekday = date.weekday()
        fits_weekly_schedule = AvailabilityRange.objects.filter(
            period__doctor=doctor,
            period__active_from__lte=date,
            day_of_week=weekday,
            start_time__lte=start_time,
            end_time__gte=end_time,
        ).filter(
            Q(period__active_until__isnull=True) | Q(period__active_until__gte=date)
        ).exists()

        fits_custom_time = CustomAvailability.objects.filter(
            doctor=doctor,
            date=date,
            start_time__lte=start_time,
            end_time__gte=end_time,
        ).exists()

        if not fits_weekly_schedule and not fits_custom_time:
            raise serializers.ValidationError(
                "This doctor isn't available at that date/time."
            )

        already_booked = (
            Appointment.objects.filter(doctor=doctor, date=date, start_time=start_time)
            .exclude(status="cancelled")
            .exists()
        )

        if already_booked:
            raise serializers.ValidationError("This slot has already been booked.")

        return data

    def create(self, validated_data):
        doctor = validated_data["doctor"]
        if doctor.fee_enabled:
            validated_data["fee_amount"] = doctor.fee_amount
            validated_data["payment_status"] = "pending"
        else:
            validated_data["payment_status"] = "not_required"
        return super().create(validated_data)


class AppointmentDetailSerializer(serializers.ModelSerializer):
    doctor_name = serializers.SerializerMethodField()
    doctor_specialty = serializers.CharField(source="doctor.get_doctor_type_display")
    doctor_clinic = serializers.CharField(source="doctor.provider.employer")

    class Meta:
        model = Appointment
        fields = [
            "id", "doctor", "doctor_name", "doctor_specialty", "doctor_clinic",
            "date", "start_time", "end_time", "reason", "reason_note",
            "patient_name", "patient_phone", "patient_email",
            "status", "payment_status", "fee_amount", "tx_ref",
        ]

    def get_doctor_name(self, obj):
        user = obj.doctor.provider.user
        return f"{user.first_name} {user.last_name}".strip()





