from django.urls import path
from .views import PriceUploadListCreateAPI

urlpatterns = [
    path("uploads/", PriceUploadListCreateAPI.as_view()),
]
