from django.urls import path
from .views import farmer_profile, farmer_profile_delete_image

urlpatterns = [
    path("profile/<int:user_id>/", farmer_profile),
     path('api/farmer/profile/<int:user_id>/delete-image/', farmer_profile_delete_image)
]