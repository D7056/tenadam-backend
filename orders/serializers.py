from rest_framework import serializers
from orders.models import OrderItem,Order, Item
from rest_framework.exceptions import PermissionDenied

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=OrderItem
        fields= ["title", "price", "quantity", "dosage"]

class OrderSerializer(serializers.ModelSerializer):
    items=OrderItemSerializer(many=True)

    class Meta:
        model= Order
        fields = ["id", "provider", "status", "created_at", "items"]
        read_only_fields=["status",'created_at']
    def create(self, validated_data):
        items_data=validated_data.pop("items")
        customer=self.context["request"].user
        order=Order.objects.create(customer=customer, **validated_data)



        for item_data in items_data:
            item= Item.objects.get(pk=item_data["item_id"])
            OrderItem.objects.create(order=order, 
                                     item=item,
                                     title=item.name,
                                    price=item.price,          # server's price, not the client's
                                    quantity=item_data["quantity"],
                                    dosage=item_data.get("dosage", ""))
        
        return order

class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model=Order
        fields=["id",'status']
        read_only_fields=["id"]
class GetItemsSerializer(serializers.ModelSerializer):
    dealer_name=serializers.CharField(source="dealer.user.first_name", read_only=True)

    class Meta:
        model=Item
        fields = ["id", "dealer", "dealer_name", "name", "price", "quantity", "dosages", "img_url"]
class GetInventorySerializer(serializers.ModelSerializer):

    class Meta:
        model=Item
        fields=["id", "name", "price","quantity", "dosages", "img_url"]

class AddToInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Item
        fields=["id", "name", "price","quantity", "dosages", "img_url"]
    
    def create(self, validated_data):
        user=self.context["request"].user

        if not hasattr(user, "provider_profile"):
            raise PermissionDenied("None Providers don't have access")
        

        return Item.objects.create(dealer=user.provider_profile, **validated_data)




