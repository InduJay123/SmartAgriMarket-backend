from django.urls import path
from .views import place_order, buyer_orders, farmer_orders

urlpatterns = [
    path('place/',place_order),
    path('buyer/<int:buyer_id>/', buyer_orders),
    path('farmer/<int:farmer_id>/', farmer_orders)
]