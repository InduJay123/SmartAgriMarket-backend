"""
URLs for ML API.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PredictionHistoryViewSet,
    ModelMetadataViewSet,
    yield_predict,
    price_predict,
    demand_predict,
    prediction_explain,
)

router = DefaultRouter()
router.register(r'history', PredictionHistoryViewSet, basename='prediction-history')
router.register(r'models', ModelMetadataViewSet, basename='model-metadata')

urlpatterns = [
    path('', include(router.urls)),
    path('predict/yield/', yield_predict, name='yield-predict'),
    path('predict/price/', price_predict, name='price-predict'),
    path('predict/demand/', demand_predict, name='demand-predict'),
    path('explain/', prediction_explain, name='prediction-explain'),
]
