"""
Admin configuration for ML API.
"""

from django.contrib import admin
from .models import PredictionHistory, ModelMetadata


@admin.register(PredictionHistory)
class PredictionHistoryAdmin(admin.ModelAdmin):
    """Admin interface for prediction history."""

    list_display = ['prediction_type', 'crop_name', 'predicted_value', 'created_at']
    list_filter = ['prediction_type', 'created_at']
    search_fields = ['crop_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ModelMetadata)
class ModelMetadataAdmin(admin.ModelAdmin):
    """Admin interface for model metadata."""

    list_display = ['model_type', 'model_version', 'accuracy', 'is_active', 'last_trained']
    list_filter = ['is_active', 'model_type']
    search_fields = ['model_type']
    readonly_fields = ['created_at', 'updated_at']
