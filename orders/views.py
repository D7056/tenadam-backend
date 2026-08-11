from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from orders.serializers import OrderSerializer, OrderStatusSerializer, GetItemsSerializer, GetInventorySerializer, AddToInventorySerializer
from orders.models import Order, Item
# Create your views here.

class OrdersCreateView(generics.CreateAPIView):
    serializer_class=OrderSerializer
    permission_classes=[permissions.IsAuthenticated]

class MyOrdersView(generics.ListAPIView):
    serializer_class=OrderSerializer
    permission_classes=[permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)

class ProviderOrderView(generics.ListAPIView):
    serializer_class=OrderSerializer
    permission_classes=[permissions.IsAuthenticated]

    def get_queryset(self):
        user=self.request.user
        if not hasattr(user, "provider_profile"):
            raise PermissionDenied("Only providers are granted access!")
        return Order.objects.filter(provider=user.provider_profile)
class UpdateOrderStatusView(generics.UpdateAPIView):
    serializer_class=OrderStatusSerializer
    permission_classes=[permissions.IsAuthenticated]

    def get_queryset(self):
        user=self.request.user
        if not hasattr(user,'provider_profile'):
            return Order.objects.none()
        return Order.objects.filter(provider=user.provider_profile)
class GetItemsView(generics.ListAPIView):
    serializer_class=GetItemsSerializer
    def get_queryset(self):
        return Item.objects.all()

class GetInventoryView(generics.ListAPIView):
    serializer_class=GetInventorySerializer
    permission_classes=[permissions.IsAuthenticated]

    def get_queryset(self):
        user=self.request.user

        if not hasattr(user,"provider_profile"):
            raise PermissionDenied("You are not a provider.")


        
        return Item.objects.filter(dealer=user.provider_profile)
class AddToInventoryView(generics.CreateAPIView):
    serializer_class=AddToInventorySerializer
    permission_classes=[permissions.IsAuthenticated]

class EditInventoryView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class=GetInventorySerializer
    permission_classes=[permissions.IsAuthenticated]

    def get_queryset(self):
        user=self.request.user

        if not hasattr(user,"provider_profile"):
            raise PermissionDenied("You are not a provider.")
        
        return Item.objects.filter(dealer=user.provider_profile)


    
    






