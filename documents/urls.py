from django.urls import path
from .views import get_priceList, upload_price_list, delete_price_list

urlpatterns = [
    path('price-lists/', get_priceList, name='price-lists'),
    path('price-list/upload/', upload_price_list),
    path('admin/price-list/<int:price_list_id>/', delete_price_list, name='admin-delete-price-list'),
]