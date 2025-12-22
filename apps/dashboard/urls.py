
from django.urls import path
from .views import admin_stats

urlpatterns = [
    path('stats/', admin_stats),
]
