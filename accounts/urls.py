from django.urls import path
from .views import SignupAPI, LoginAPI, FarmerProfileAPI, DeleteProfileImageAPI

urlpatterns = [
    path('signup/', SignupAPI.as_view()),
    path('login/', LoginAPI.as_view()),
    path('farmer/profile/', FarmerProfileAPI.as_view(), name="farmer-profile"),
    path('farmer/profile/image/', DeleteProfileImageAPI.as_view(), name='delete-profile-image')

]
