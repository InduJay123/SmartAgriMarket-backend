from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from accounts.views import UserViewSet
from mcrops.views import CropViewSet
from pricing.views import PriceRecordViewSet

router = DefaultRouter()
router.register("users", UserViewSet)
router.register("crops", CropViewSet)
router.register("prices", PriceRecordViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
]
