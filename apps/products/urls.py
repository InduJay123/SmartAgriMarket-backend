from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, ListingViewSet
from django.urls import path, include

router = DefaultRouter()
router.register('products', ProductViewSet, basename='product')
router.register('listings', ListingViewSet, basename='listing')

urlpatterns = [
    path('', include(router.urls)),
]
