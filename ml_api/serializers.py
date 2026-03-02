"""
ML API Serializers

Serializers for the ML prediction API endpoints.
"""

from rest_framework import serializers


class FloodPredictionInputSerializer(serializers.Serializer):
    """
    Serializer for flood prediction input data.
    
    Contains all the features needed for flood risk prediction.
    """
    
    # Location features
    district = serializers.CharField(required=False, default='Colombo')
    latitude = serializers.FloatField(required=False, default=6.9271)
    longitude = serializers.FloatField(required=False, default=79.8612)
    elevation_m = serializers.FloatField(required=False, default=0)
    distance_to_river_m = serializers.FloatField(required=False, default=1000)
    urban_rural = serializers.CharField(required=False, default='Urban')
    
    # Infrastructure features
    landcover = serializers.CharField(required=False, default='Urban')
    soil_type = serializers.CharField(required=False, default='Clay')
    water_supply = serializers.CharField(required=False, default='Municipal')
    electricity = serializers.CharField(required=False, default='Yes')
    road_quality = serializers.CharField(required=False, default='Good')
    infrastructure_score = serializers.FloatField(required=False, default=50)
    population_density_per_km2 = serializers.FloatField(required=False, default=1000)
    built_up_percent = serializers.FloatField(required=False, default=50)
    
    # Environmental features
    ndvi = serializers.FloatField(required=False, default=0.3)
    drainage_index = serializers.FloatField(required=False, default=0.5)
    
    # Weather features
    precipitation_sum = serializers.FloatField(required=False, default=0)
    rainfall_7d = serializers.FloatField(required=False, default=0)
    rainfall_14d = serializers.FloatField(required=False, default=0)
    rainfall_30d = serializers.FloatField(required=False, default=0)
    monthly_rainfall_mm = serializers.FloatField(required=False, default=0)
    temperature_2m_mean = serializers.FloatField(required=False, default=28)
    temp_avg_7d = serializers.FloatField(required=False, default=28)
    windspeed_10m_max = serializers.FloatField(required=False, default=10)
    windspeed_max_7d = serializers.FloatField(required=False, default=10)
    weathercode = serializers.IntegerField(required=False, default=0)
    precipitation_hours = serializers.FloatField(required=False, default=0)
    
    # Historical features
    historical_flood_count = serializers.IntegerField(required=False, default=0)
    
    # Temporal features
    month = serializers.IntegerField(required=False, min_value=1, max_value=12, default=1)
    is_monsoon = serializers.IntegerField(required=False, min_value=0, max_value=1, default=0)
    
    def to_features_dict(self):
        """Convert validated data to features dictionary for prediction."""
        return dict(self.validated_data)


class FloodPredictionOutputSerializer(serializers.Serializer):
    """Serializer for flood prediction output."""
    
    flood_predicted = serializers.BooleanField()
    flood_probability = serializers.FloatField()
    risk_level = serializers.CharField()
    no_flood_probability = serializers.FloatField()
    confidence = serializers.FloatField()


class FloodPredictionResponseSerializer(serializers.Serializer):
    """Complete response serializer for flood prediction."""
    
    success = serializers.BooleanField()
    message = serializers.CharField()
    prediction = FloodPredictionOutputSerializer(required=False, allow_null=True)
    error = serializers.CharField(required=False, allow_null=True)


class BatchFloodPredictionInputSerializer(serializers.Serializer):
    """Serializer for batch flood prediction input."""
    
    locations = FloodPredictionInputSerializer(many=True)


class BatchFloodPredictionResponseSerializer(serializers.Serializer):
    """Serializer for batch flood prediction response."""
    
    success = serializers.BooleanField()
    message = serializers.CharField()
    predictions = FloodPredictionOutputSerializer(many=True, required=False)
    count = serializers.IntegerField(required=False)
    error = serializers.CharField(required=False, allow_null=True)


class FeatureImportanceSerializer(serializers.Serializer):
    """Serializer for feature importance output."""
    
    feature = serializers.CharField()
    importance = serializers.FloatField()


class ModelInfoSerializer(serializers.Serializer):
    """Serializer for model information."""
    
    status = serializers.CharField()
    model_type = serializers.CharField(required=False)
    has_scaler = serializers.BooleanField(required=False)
    has_encoders = serializers.BooleanField(required=False)
    has_feature_info = serializers.BooleanField(required=False)
    n_estimators = serializers.IntegerField(required=False)
    max_depth = serializers.IntegerField(required=False, allow_null=True)
    n_features = serializers.IntegerField(required=False)
    error = serializers.CharField(required=False, allow_null=True)
