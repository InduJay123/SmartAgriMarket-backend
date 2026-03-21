from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CropViewSet

router = DefaultRouter()
router.register(r'', CropViewSet, basename='crops')

urlpatterns = [
    path('', include(router.urls)),
]
