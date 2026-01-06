"""
URLs for ML API.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PredictionHistoryViewSet,
    ModelMetadataViewSet,
    YieldPredictionView,
    PricePredictionView,
    DemandPredictionView,
    PredictionExplainerView,
)

router = DefaultRouter()
router.register(r'history', PredictionHistoryViewSet, basename='prediction-history')
router.register(r'models', ModelMetadataViewSet, basename='model-metadata')

urlpatterns = [
    path('', include(router.urls)),
    path('predict/yield/', YieldPredictionView.predict, name='yield-predict'),
    path('predict/price/', PricePredictionView.predict, name='price-predict'),
    path('predict/demand/', DemandPredictionView.predict, name='demand-predict'),
    path('explain/', PredictionExplainerView.explain, name='prediction-explain'),
]
