"""
ML API URLs

URL routing for machine learning prediction API endpoints.
"""

from django.urls import path
from . import views

app_name = 'ml_api'

urlpatterns = [
    # Health check endpoint
    path('health/', views.health_check, name='health_check'),
    
    # Flood prediction endpoints
    path('flood/predict/', views.FloodPredictionView.as_view(), name='flood_predict'),
    path('flood/predict/batch/', views.BatchFloodPredictionView.as_view(), name='flood_predict_batch'),
    path('flood/model-info/', views.ModelInfoView.as_view(), name='model_info'),
    path('flood/feature-importance/', views.FeatureImportanceView.as_view(), name='feature_importance'),
]
