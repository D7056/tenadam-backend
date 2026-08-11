from django.urls import path
from orders.views import OrdersCreateView, MyOrdersView, ProviderOrderView, UpdateOrderStatusView, GetItemsView, GetInventoryView, AddToInventoryView, EditInventoryView
urlpatterns=[path("",OrdersCreateView.as_view(), name="order-create"), 
             path("incoming/",ProviderOrderView.as_view()),
               path("my-orders/", MyOrdersView.as_view() ),
               path("<int:pk>/status/", UpdateOrderStatusView.as_view() ),
               path("items/", GetItemsView.as_view()),
               path("inventory/", GetInventoryView.as_view()),
               path("inventory/add/", AddToInventoryView.as_view()),
               path("inventory/<int:pk>/", EditInventoryView.as_view())]
