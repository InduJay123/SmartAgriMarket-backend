from django.urls import path
from .views import SignupAPI, LoginAPI, FarmerProfileAPI, DeleteProfileImageAPI, BuyerProfileAPI,DeleteBuyerProfileImageAPI, ForgotPasswordAPIView, ResetPasswordAPIView

urlpatterns = [
    path('signup/', SignupAPI.as_view()),
    path('login/', LoginAPI.as_view()),
    path('farmer/profile/', FarmerProfileAPI.as_view(), name="farmer-profile"),
    path('farmer/profile/image/', DeleteProfileImageAPI.as_view(), name='delete-profile-image'),
    path('buyer/profile/', BuyerProfileAPI.as_view(), name="buyer-profile"),
    path('buyer/profile/image/', DeleteBuyerProfileImageAPI.as_view(), name='delete-buyer-profile-image'),

    path("forgot-password/", ForgotPasswordAPIView.as_view()),
    path("reset-password/", ResetPasswordAPIView.as_view()),
]
