from django.urls import path
from .views import (
    PendingUsersView,
    ApproveUserView,
    RejectUserView,
    FarmerListView,
    FarmerDetailView,
    BlockFarmerView,
    UnblockFarmerView,
    DeleteFarmerView,
    BuyerListView,
    BuyerDetailView,
    BlockBuyerView,
    UnblockBuyerView,
    DeleteBuyerView
    )

urlpatterns = [
    path('pending-users/', PendingUsersView.as_view()),
    path('users/<int:user_id>/approve/', ApproveUserView.as_view()),
    path('users/<int:user_id>/reject/', RejectUserView.as_view()),
    path('farmers/', FarmerListView.as_view()),
    path('farmers/<int:pk>/', FarmerDetailView.as_view()),
    path('farmers/<int:farmer_id>/block/', BlockFarmerView.as_view()),
    path('farmers/<int:farmer_id>/unblock/', UnblockFarmerView.as_view()),
    path('farmers/<int:farmer_id>/delete/', DeleteFarmerView.as_view()),
    path('buyers/', BuyerListView.as_view()),
    path('buyers/<int:pk>/', BuyerDetailView.as_view()),
    path('buyers/<int:buyer_id>/block/', BlockBuyerView.as_view()),
    path('buyers/<int:buyer_id>/unblock/', UnblockBuyerView.as_view()),
    path('buyers/<int:buyer_id>/delete/', DeleteBuyerView.as_view()),
]
