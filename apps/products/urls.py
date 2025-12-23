from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, ListingViewSet, tomato_price_chart
from django.urls import path, include

from .views import (
    AdminCropListCreateView,
    AdminCropUpdateView,
    AdminCropDeleteView,
)

router = DefaultRouter()
router.register('products', ProductViewSet, basename='product')
router.register('listings', ListingViewSet, basename='listing')

urlpatterns = [
    path('', include(router.urls)),
    path('tomato-price-chart/', tomato_price_chart),
    path('crops/', AdminCropListCreateView.as_view()),
    path('crops/<int:pk>/', AdminCropUpdateView.as_view()),
    path('crops/<int:crop_id>/delete/', AdminCropDeleteView.as_view()),
]
