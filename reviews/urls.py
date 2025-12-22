from django.urls import path
from .views import get_reviews, add_review

urlpatterns = [
    path('product/<int:product_id>/', get_reviews),
    path('add/', add_review),
]