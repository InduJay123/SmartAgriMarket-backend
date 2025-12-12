from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import OrderViewSet, TransactionViewSet, payment_webhook

router = DefaultRouter()
router.register('orders', OrderViewSet, basename='order')
router.register('transactions', TransactionViewSet, basename='transaction')

urlpatterns = [
    path('', include(router.urls)),
    path('payments/webhook/', payment_webhook, name='payments-webhook'),
]
