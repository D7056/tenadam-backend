from django.shortcuts import render
from django.db.models import Q
from rest_framework import generics
from .serializer import RegisterSerializer, LoginSerializer, ProviderSerializer, ProviderProfileSerializer, GetUserSerializer, CompleteProfileSerializer, DoctorListSerializer
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from accounts.models import ProviderProfile, User
import requests
# Create your views here.

class RegisterView(generics.CreateAPIView):
    serializer_class=RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "id": user.id,
                "phone_number": user.phone_number,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "roles": user.roles,
                "profile_completed": user.profile_completed,
            },
            status=status.HTTP_201_CREATED,
        )

class LoginView(APIView):
    def post(self, request):

        serializer=LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=serializer.validated_data["user"]
        service_type=serializer.validated_data["service_type"]



        token, _ = Token.objects.get_or_create(user=user)



        return Response({"token": token.key,
                         "roles": user.roles,
                         "id": user.id,
                         'service_type':service_type,
                         "first_name":user.first_name,
                         "last_name": user.last_name,
                         'phone_number':user.phone_number,
                         "email": user.email,
                         "profile_completed": user.profile_completed,
                         })
class MeView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request):
        user=request.user
        return Response(
            {
            "id": user.id,
            "phone_number": user.phone_number,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "roles": user.roles,}
        )
class ProviderRegisterView(generics.CreateAPIView):
    serializer_class=ProviderSerializer

    def create(self,request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token, _ = Token.objects.get_or_create(user=user)

        
        return Response(
            {
                "token": token.key,
                "user": serializer.data,
                "roles": user.roles,
                "profile_completed": user.profile_completed,
            },
            status=status.HTTP_201_CREATED,
        )
        

class ProviderListView(generics.ListAPIView):
    serializer_class=ProviderProfileSerializer
    queryset=ProviderProfile.objects.filter(service_type="medicine_dealer", approved=True)

class DoctorListView(generics.ListAPIView):
    serializer_class=DoctorListSerializer
    queryset=ProviderProfile.objects.filter(
        service_type="doctor",
        approved=True,
    ).filter(
        Q(doctor__availability_periods__isnull=False)
        | Q(doctor__custom_times__isnull=False)
    ).distinct()


class ProviderLoginView(APIView):
    def post(self, request):

        serializer=LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=serializer.validated_data["user"]

        token, _ = Token.objects.get_or_create(user=user)



        return Response({
            "token": token.key,
            "roles": user.roles,
            "id": user.id,
            "profile_completed": user.profile_completed,
        })

class EditProfile(generics.UpdateAPIView):
    serializer_class=GetUserSerializer
    permission_classes=[IsAuthenticated]

    def get_object(self):
        return self.request.user

class CompleteProfileView(generics.GenericAPIView):
    serializer_class=CompleteProfileSerializer
    permission_classes=[IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "address": user.address,
            "profile_completed": user.profile_completed,
        })
    

    


class DrugImageView(APIView):
    def get(self, request):
        set_id = request.query_params.get("set_id")
        if not set_id:
            return Response({"error": "set_id is required"}, status=400)

        url = f"https://dailymed.nlm.nih.gov/dailymed/services/v2/spls/{set_id}/media.json"

        try:
            response = requests.get(url, timeout=5)
        except requests.RequestException:
            return Response({"image_url": None})

        if not response.ok:
            return Response({"image_url": None})

        try:
            data = response.json()
            media = data.get("data", {}).get("media", [])
            image_url = media[0]["url"] if media else None
        except (ValueError, KeyError, IndexError):
            image_url = None

        return Response({"image_url": image_url})











