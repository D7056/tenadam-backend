from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from causes.models import Cause
from causes.serializers import CauseSerializer, CreateCauseSerializer


class CauseListView(generics.ListAPIView):
    serializer_class = CauseSerializer
    queryset = Cause.objects.filter(approved=True).order_by("-created_at")


class SubmitCauseView(generics.CreateAPIView):
    serializer_class = CreateCauseSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]


class MyCausesView(generics.ListAPIView):
    serializer_class = CauseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cause.objects.filter(submitted_by=self.request.user).order_by("-created_at")


class CauseDetailView(generics.RetrieveAPIView):
    serializer_class = CauseSerializer
    queryset = Cause.objects.filter(approved=True)
