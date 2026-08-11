from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, ProviderProfile
from appointments.models import Doctor
from appointments.choices import DOCTOR_TYPE_CHOICES

class LoginSerializer(serializers.Serializer):
    password=serializers.CharField(write_only=True, min_length=8)
    phone_number=serializers.CharField()

    

    def validate(self, data):
        user=authenticate(phone_number=data["phone_number"], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid phone number or passowrd!")
        
        data['user']=user



        profile=getattr(user, "provider_profile", None)

        if not profile:
            
            data['service_type']=None
        
        else:

            service_type=user.provider_profile.service_type
            data["service_type"]=service_type

        return data

    
    

    
class RegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model=User
        fields=["id", "phone_number", "password","email", "first_name", "last_name","roles"]
        

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class ProviderSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True, min_length=8)
    service_type= serializers.ChoiceField(
        choices=ProviderProfile.SERVICE_TYPE_CHOICES, write_only=True
    )
    doctor_type = serializers.ChoiceField(
        choices=DOCTOR_TYPE_CHOICES, write_only=True, required=False
    )

    class Meta:
        model=User
        fields=["id", "phone_number", "password","email", "first_name", "last_name","service_type","doctor_type"]
    
    def validate(self, data):
        if data.get("service_type") == "doctor" and not data.get("doctor_type"):
            raise serializers.ValidationError({"doctor_type": "This field is required for doctors."})
        return data
    
    def create(self, validated_data):
        service_type = validated_data.pop("service_type")
        doctor_type = validated_data.pop("doctor_type", None)
        validated_data['roles'] = 'provider'
        user = User.objects.create_user(**validated_data)
        provider_profile = ProviderProfile.objects.create(user=user, service_type=service_type)
        if service_type == "doctor":
            Doctor.objects.create(provider=provider_profile, doctor_type=doctor_type)
        return user
class ProviderProfileSerializer(serializers.ModelSerializer):
    phone_number=serializers.CharField(source="user.phone_number")
    first_name=serializers.CharField(source='user.first_name')
    last_name=serializers.CharField(source='user.last_name')

    class Meta:
        model=ProviderProfile
        fields = ["id", "first_name", "last_name", "phone_number", "service_type", "approved"]

class DoctorListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="doctor.id")
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    specialty = serializers.CharField(source="doctor.get_doctor_type_display")
    clinic = serializers.CharField(source="employer")

    class Meta:
        model = ProviderProfile
        fields = ["id", "first_name", "last_name", "specialty", "clinic"]

class GetUserSerializer(serializers.ModelSerializer):

    class Meta:
        model=User
        fields=["id", "first_name", "last_name", "phone_number"]


class CompleteProfileSerializer(serializers.Serializer):
    region = serializers.CharField(max_length=100)
    city = serializers.CharField(max_length=100)
    address_line = serializers.CharField(max_length=150)
    employer = serializers.CharField(max_length=50, required=False, allow_blank=True)

    def save(self):
        user = self.context["request"].user
        data = self.validated_data

        user.address = f"{data['region']}, {data['city']}, {data['address_line']}"
        user.profile_completed = True
        user.save()

        provider_profile = getattr(user, "provider_profile", None)
        if provider_profile is not None:
            employer = data.get("employer", "").strip()
            provider_profile.employer = employer or "self-employed"
            provider_profile.save()

        return user




    
        