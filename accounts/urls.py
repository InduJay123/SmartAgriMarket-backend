from django.urls import path
from .views import SignupAPI, LoginAPI, FarmerProfileAPI,DeleteProfileImageAPI, BuyerProfileAPI,DeleteBuyerProfileImageAPI,ForgotPasswordAPIView, ResetPasswordAPIView
from .admin_views import AdminFarmersListAPI, AdminBuyersListAPI, AdminVerifyUserAPI, AdminLoginAPI, AdminDashboardStatsAPI, AdminDashboardChartsAPI, AdminUserDetailAPI, AdminPendingUsersAPI
from .admin_settings_views import AdminSettingsAPI, AdminChangePasswordAPI



urlpatterns = [
    path('signup/', SignupAPI.as_view()),
    path('login/', LoginAPI.as_view()),
    path('farmer/profile/', FarmerProfileAPI.as_view(), name="farmer-profile"),
    path('farmer/profile/image/', DeleteProfileImageAPI.as_view(), name='delete-profile-image'),
    path('buyer/profile/', BuyerProfileAPI.as_view(), name="buyer-profile"),
    path('buyer/profile/image/', DeleteBuyerProfileImageAPI.as_view(), name='delete-buyer-profile-image'),

    path("forgot-password/", ForgotPasswordAPIView.as_view()),
    path("reset-password/", ResetPasswordAPIView.as_view()),

    path("admin/login/", AdminLoginAPI.as_view()),
    path("admin/farmers/", AdminFarmersListAPI.as_view()),
    path("admin/buyers/", AdminBuyersListAPI.as_view()),
    path("admin/verify/", AdminVerifyUserAPI.as_view()),
    path("admin/pending-users/", AdminPendingUsersAPI.as_view()),
    path("admin/dashboard-stats/", AdminDashboardStatsAPI.as_view()),
    path("admin/dashboard-charts/", AdminDashboardChartsAPI.as_view()),
    path("admin/user/<int:user_id>/", AdminUserDetailAPI.as_view()),
    path("admin/settings/", AdminSettingsAPI.as_view()),
    path("admin/change-password/", AdminChangePasswordAPI.as_view()),

    

]
