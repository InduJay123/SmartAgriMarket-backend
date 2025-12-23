from django.urls import path
from .views import get_available_products,toggle_favourite, get_favourites,get_buyer_profile,update_buyer_profile,delete_buyer_profile_image


urlpatterns = [
    path('products/', get_available_products, name='available_products'),
    path('favourites/', get_favourites, name='get_favourites'),
    path('favourites/toggle/', toggle_favourite, name='toggle_favourite'),
    path('buyer/profile/<int:user_id>/', get_buyer_profile),
    path('buyer/profile/<int:user_id>/update/', update_buyer_profile),
    path('buyer/profile-image/<int:user_id>/', delete_buyer_profile_image, name='delete-buyer-profile-image')
]
