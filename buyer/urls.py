from django.urls import path
from .views import get_available_products,toggle_favourite, get_favourites


urlpatterns = [
    path('products/', get_available_products, name='available_products'),
    path('favourites/', get_favourites, name='get_favourites'),
    path('favourites/toggle/', toggle_favourite, name='toggle_favourite'),
]
