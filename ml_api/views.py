"""
Views for ML API.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
import logging

from .models import PredictionHistory, ModelMetadata
from .serializers import (
    PredictionHistorySerializer,
    ModelMetadataSerializer,
    YieldPredictionRequestSerializer,
    PricePredictionRequestSerializer,
    DemandPredictionRequestSerializer,
)
from ml_models.predictors import YieldPredictor, PricePredictor, DemandPredictor
from ml_models.utils.logger import setup_logger

logger = setup_logger(__name__)


class PredictionHistoryViewSet(viewsets.ModelViewSet):
    """ViewSet for prediction history."""

    queryset = PredictionHistory.objects.all()
    serializer_class = PredictionHistorySerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get predictions filtered by type."""
        pred_type = request.query_params.get('type')
        if not pred_type:
            return Response(
                {'error': 'type parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        predictions = self.queryset.filter(prediction_type=pred_type)
        serializer = self.get_serializer(predictions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_crop(self, request):
        """Get predictions filtered by crop."""
        crop_name = request.query_params.get('crop')
        if not crop_name:
            return Response(
                {'error': 'crop parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        predictions = self.queryset.filter(crop_name__icontains=crop_name)
        serializer = self.get_serializer(predictions, many=True)
        return Response(serializer.data)


class ModelMetadataViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for model metadata."""

    queryset = ModelMetadata.objects.filter(is_active=True)
    serializer_class = ModelMetadataSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def active_models(self, request):
        """Get all active models."""
        models = self.queryset.all()
        serializer = self.get_serializer(models, many=True)
        return Response(serializer.data)


class YieldPredictionView:
    """View for yield predictions."""

    @staticmethod
    def predict(request):
        """Predict crop yield."""
        serializer = YieldPredictionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            predictor = YieldPredictor()
            features = serializer.validated_data
            prediction = predictor.predict(features)

            # Store prediction history
            PredictionHistory.objects.create(
                prediction_type='yield',
                crop_name=features['crop_type'],
                input_features=features,
                predicted_value=prediction,
            )

            logger.info(f"Yield prediction made for {features['crop_type']}")
            return Response({
                'prediction_type': 'yield',
                'crop_type': features['crop_type'],
                'predicted_yield': prediction,
                'unit': 'kg/hectare',
            })
        except Exception as e:
            logger.error(f"Error in yield prediction: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PricePredictionView:
    """View for price predictions."""

    @staticmethod
    def predict(request):
        """Predict crop price."""
        serializer = PricePredictionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            predictor = PricePredictor()
            features = serializer.validated_data
            prediction = predictor.predict(features)

            # Store prediction history
            PredictionHistory.objects.create(
                prediction_type='price',
                crop_name=features['crop_type'],
                input_features=features,
                predicted_value=prediction,
            )

            logger.info(f"Price prediction made for {features['crop_type']}")
            return Response({
                'prediction_type': 'price',
                'crop_type': features['crop_type'],
                'predicted_price': prediction,
                'currency': 'LKR',
            })
        except Exception as e:
            logger.error(f"Error in price prediction: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DemandPredictionView:
    """View for demand predictions."""

    @staticmethod
    def predict(request):
        """Predict crop demand."""
        serializer = DemandPredictionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            predictor = DemandPredictor()
            features = serializer.validated_data
            prediction = predictor.predict(features)

            # Store prediction history
            PredictionHistory.objects.create(
                prediction_type='demand',
                crop_name=features['crop_type'],
                input_features=features,
                predicted_value=prediction,
            )

            logger.info(f"Demand prediction made for {features['crop_type']}")
            return Response({
                'prediction_type': 'demand',
                'crop_type': features['crop_type'],
                'predicted_demand': prediction,
                'unit': 'tonnes',
            })
        except Exception as e:
            logger.error(f"Error in demand prediction: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
