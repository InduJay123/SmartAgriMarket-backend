from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CropViewSet,
    MarketplaceViewSet,
    get_available_products,
    get_favourites,
    toggle_favourite,
)

router = DefaultRouter()
router.register(r'crops', CropViewSet, basename='crops')
router.register(r'marketplace', MarketplaceViewSet, basename='marketplace')

urlpatterns = [
    path('', include(router.urls)),
    path('products/', get_available_products, name='available_products'),
    path('favourites/', get_favourites, name='get_favourites'),
    path('favourites/toggle/<int:market_id>/',
        toggle_favourite,
        name='toggle_favourite'
    ),
]
