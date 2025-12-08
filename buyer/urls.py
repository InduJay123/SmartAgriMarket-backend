from django.urls import path
from .views import get_available_products

urlpatterns = [
    path('products/', get_available_products, name='available_products'),
]
