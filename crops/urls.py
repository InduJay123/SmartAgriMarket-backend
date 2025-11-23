from rest_framework.routers import DefaultRouter
from .views import CropViewSet, MarketplaceViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'crops', CropViewSet)
router.register(r'marketplace', MarketplaceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
