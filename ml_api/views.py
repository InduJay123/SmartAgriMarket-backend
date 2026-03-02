"""
ML API Views

API views for machine learning prediction endpoints.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

# Try to import drf_yasg for swagger documentation
try:
    from drf_yasg.utils import swagger_auto_schema
    from drf_yasg import openapi
    HAS_SWAGGER = True
except ImportError:
    HAS_SWAGGER = False
    # Create dummy decorator if drf_yasg is not installed
    def swagger_auto_schema(**kwargs):
        def decorator(func):
            return func
        return decorator

from .serializers import (
    FloodPredictionInputSerializer,
    FloodPredictionResponseSerializer,
    BatchFloodPredictionInputSerializer,
    BatchFloodPredictionResponseSerializer,
    ModelInfoSerializer,
)

import sys
import os

# Add ml_models to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ml_models.predictors.flood_predictor import get_predictor
except ImportError:
    # Fallback if import fails
    get_predictor = None


class FloodPredictionView(APIView):
    """
    Flood Risk Prediction API
    
    Predicts flood risk for a given location based on weather, environmental,
    and infrastructure features.
    """
    
    @swagger_auto_schema(
        operation_description="Predict flood risk for a given location",
        request_body=FloodPredictionInputSerializer,
        responses={
            200: FloodPredictionResponseSerializer,
            400: 'Bad Request',
            500: 'Internal Server Error'
        },
        tags=['Flood Prediction']
    )
    def post(self, request):
        """
        Predict flood risk for a single location.
        
        Send location, weather, and environmental features to get
        flood risk prediction including probability and risk level.
        """
        serializer = FloodPredictionInputSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Invalid input data',
                'error': serializer.errors,
                'prediction': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            if get_predictor is None:
                return Response({
                    'success': False,
                    'message': 'Prediction service unavailable',
                    'error': 'Model predictor not initialized',
                    'prediction': None
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            predictor = get_predictor()
            features = serializer.to_features_dict()
            prediction = predictor.predict(features)
            
            return Response({
                'success': True,
                'message': 'Flood prediction successful',
                'prediction': prediction,
                'error': None
            }, status=status.HTTP_200_OK)
            
        except FileNotFoundError as e:
            return Response({
                'success': False,
                'message': 'Model not found',
                'error': str(e),
                'prediction': None
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Prediction failed',
                'error': str(e),
                'prediction': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BatchFloodPredictionView(APIView):
    """
    Batch Flood Risk Prediction API
    
    Predicts flood risk for multiple locations in a single request.
    """
    
    @swagger_auto_schema(
        operation_description="Predict flood risk for multiple locations",
        request_body=BatchFloodPredictionInputSerializer,
        responses={
            200: BatchFloodPredictionResponseSerializer,
            400: 'Bad Request',
            500: 'Internal Server Error'
        },
        tags=['Flood Prediction']
    )
    def post(self, request):
        """
        Predict flood risk for multiple locations.
        
        Send an array of locations with their features to get
        flood risk predictions for each location.
        """
        serializer = BatchFloodPredictionInputSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Invalid input data',
                'error': serializer.errors,
                'predictions': [],
                'count': 0
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            if get_predictor is None:
                return Response({
                    'success': False,
                    'message': 'Prediction service unavailable',
                    'error': 'Model predictor not initialized',
                    'predictions': [],
                    'count': 0
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            predictor = get_predictor()
            locations = serializer.validated_data['locations']
            
            predictions = []
            for location_data in locations:
                location_serializer = FloodPredictionInputSerializer(data=location_data)
                if location_serializer.is_valid():
                    features = location_serializer.to_features_dict()
                    prediction = predictor.predict(features)
                    predictions.append(prediction)
            
            return Response({
                'success': True,
                'message': f'Batch prediction successful for {len(predictions)} locations',
                'predictions': predictions,
                'count': len(predictions),
                'error': None
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Batch prediction failed',
                'error': str(e),
                'predictions': [],
                'count': 0
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ModelInfoView(APIView):
    """
    Model Information API
    
    Get information about the loaded flood prediction model.
    """
    
    @swagger_auto_schema(
        operation_description="Get information about the flood prediction model",
        responses={
            200: ModelInfoSerializer,
            500: 'Internal Server Error'
        },
        tags=['Flood Prediction']
    )
    def get(self, request):
        """
        Get model information including status, type, and configuration.
        """
        try:
            if get_predictor is None:
                return Response({
                    'status': 'unavailable',
                    'error': 'Model predictor not initialized'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            predictor = get_predictor()
            model_info = predictor.get_model_info()
            
            return Response(model_info, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FeatureImportanceView(APIView):
    """
    Feature Importance API
    
    Get the most important features for flood prediction.
    """
    
    def get(self, request):
        """
        Get the top N most important features for flood prediction.
        
        Query Parameters:
            top_n: Number of top features to return (default: 10)
        """
        try:
            if get_predictor is None:
                return Response({
                    'success': False,
                    'error': 'Model predictor not initialized',
                    'features': {}
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            top_n = int(request.query_params.get('top_n', 10))
            
            predictor = get_predictor()
            importance = predictor.get_feature_importance(top_n=top_n)
            
            # Convert to list format for better readability
            features_list = [
                {'feature': k, 'importance': v}
                for k, v in importance.items()
            ]
            
            return Response({
                'success': True,
                'features': features_list,
                'count': len(features_list)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'features': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def health_check(request):
    """
    Health check endpoint for the ML API.
    """
    try:
        predictor_status = 'unavailable'
        if get_predictor is not None:
            try:
                predictor = get_predictor()
                predictor_status = 'loaded' if predictor.is_loaded else 'not_loaded'
            except Exception:
                predictor_status = 'error'
        
        return Response({
            'status': 'healthy',
            'service': 'ML API',
            'flood_predictor': predictor_status
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'unhealthy',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
