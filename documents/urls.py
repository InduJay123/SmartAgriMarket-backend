from django.urls import path
from .views import get_priceList, upload_price_list

urlpatterns = [
    path('price-lists/', get_priceList, name='price-lists'),
    path('mock-upload/', upload_price_list),
]