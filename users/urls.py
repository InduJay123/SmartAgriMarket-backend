from django.urls import path
from .views import farmer_profile, farmer_profile_delete_image, login,signup

urlpatterns = [
    path("signup/", signup),
    path("login/", login),
    path("profile/<int:user_id>/", farmer_profile),
    path("profile/<int:user_id>/delete-image/", farmer_profile_delete_image)
]