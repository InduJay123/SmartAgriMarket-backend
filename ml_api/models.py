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
