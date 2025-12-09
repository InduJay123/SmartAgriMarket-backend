"""
Serializers for ML API.
"""

from rest_framework import serializers
from .models import PredictionHistory, ModelMetadata


class PredictionHistorySerializer(serializers.ModelSerializer):
    """Serializer for prediction history."""

    class Meta:
        model = PredictionHistory
        fields = [
            'id',
            'prediction_type',
            'crop_name',
            'input_features',
            'predicted_value',
            'confidence',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ModelMetadataSerializer(serializers.ModelSerializer):
    """Serializer for model metadata."""

    class Meta:
        model = ModelMetadata
        fields = [
            'id',
            'model_type',
            'model_version',
            'accuracy',
            'last_trained',
            'training_samples',
            'is_active',
            'features',
            'parameters',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class YieldPredictionRequestSerializer(serializers.Serializer):
    """Serializer for yield prediction request."""

    crop_type = serializers.CharField(max_length=100)
    rainfall = serializers.FloatField()
    temperature = serializers.FloatField()
    soil_quality = serializers.CharField(max_length=50)
    fertilizer = serializers.FloatField()
    irrigation = serializers.BooleanField()


class PricePredictionRequestSerializer(serializers.Serializer):
    """Serializer for price prediction request."""

    crop_type = serializers.CharField(max_length=100)
    season = serializers.CharField(max_length=50)
    supply = serializers.FloatField()
    demand = serializers.FloatField()
    market_trend = serializers.CharField(max_length=50)


class DemandPredictionRequestSerializer(serializers.Serializer):
    """Serializer for demand prediction request."""

    crop_type = serializers.CharField(max_length=100)
    season = serializers.CharField(max_length=50)
    historical_demand = serializers.FloatField()
    population = serializers.IntegerField()
    consumption_trend = serializers.CharField(max_length=50)
