# notifications/urls.py
from django.urls import path
from .views import register_token

urlpatterns = [
    path("save-token/", register_token),
]