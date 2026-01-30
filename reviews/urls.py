from django.urls import path
from .views import get_reviews, add_review,review_summary, farmer_rating_summary

urlpatterns = [
    path('product/<int:product_id>/', get_reviews),
    path('add/', add_review),
    path("summary/<int:market_id>/", review_summary),
    path("farmer/summary/<int:farmer_id>/", farmer_rating_summary),
]