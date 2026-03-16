"""
Models for ML API to store prediction history and model metadata.
"""

from django.db import models


class PredictionHistory(models.Model):
    """Store historical predictions for auditing and analysis."""

    PREDICTION_TYPES = [
        ('yield', 'Yield Prediction'),
        ('price', 'Price Prediction'),
        ('demand', 'Demand Prediction'),
    ]

    prediction_type = models.CharField(max_length=20, choices=PREDICTION_TYPES)
    crop_name = models.CharField(max_length=100)
    input_features = models.JSONField()
    predicted_value = models.FloatField()
    confidence = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['prediction_type', 'crop_name']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.prediction_type} - {self.crop_name} ({self.created_at})"


class ModelMetadata(models.Model):
    """Store metadata about trained models."""

    model_type = models.CharField(max_length=50, unique=True)
    model_version = models.CharField(max_length=20)
    accuracy = models.FloatField(null=True, blank=True)
    last_trained = models.DateTimeField(null=True, blank=True)
    training_samples = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    features = models.JSONField()
    parameters = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Model Metadata"

    def __str__(self):
        return f"{self.model_type} v{self.model_version}"



from django.db import models

class TrendAlert(models.Model):
    METRIC_CHOICES = [("PRICE","Price"), ("DEMAND","Demand"), ("YIELD","Yield")]
    DIRECTION_CHOICES = [("UP","Up"), ("DOWN","Down")]
    SEVERITY_CHOICES = [("LOW","Low"), ("MEDIUM","Medium"), ("HIGH","High")]
    STATUS_CHOICES = [("NEW","New"), ("NOTIFIED","Notified")]

    product = models.CharField(max_length=100, null=True, blank=True) # <-- important
  # optional if you can map
    metric = models.CharField(max_length=10, choices=METRIC_CHOICES)

    forecast_date = models.DateField()
    predicted_value = models.FloatField()

    baseline_value = models.FloatField(null=True, blank=True)
    change_pct = models.FloatField(null=True, blank=True)

    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default="MEDIUM")
    reason = models.CharField(max_length=255, null=True, blank=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="NEW")
    created_at = models.DateTimeField(auto_now_add=True)

class Meta:
    unique_together = (("product", "metric", "forecast_date", "direction"),)



from django.db import models

# No Django models for ml_api as it uses ML model files (joblib/pkl)
# The ml_api app serves as an API layer for the ML models stored in ml_models/models/
