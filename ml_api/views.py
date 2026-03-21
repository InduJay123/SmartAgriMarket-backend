from rest_framework.views import APIView

# Try to import drf_yasg for swagger documentation
try:
    from drf_yasg.utils import swagger_auto_schema
    from drf_yasg import openapi
    HAS_SWAGGER = True
except ImportError:
    HAS_SWAGGER = False
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
    FeatureImportanceSerializer
)

try:
    from ml_models.predictors.flood_predictor import get_predictor
except ImportError:
    get_predictor = None

"""
Views for ML API.
"""

import os
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import PredictionHistory, ModelMetadata
from .serializers import (
    PredictionHistorySerializer,
    ModelMetadataSerializer,
    YieldPredictionRequestSerializer,
    PricePredictionRequestSerializer,
    DemandPredictionRequestSerializer,
)


# --- FastAPI proxy for price_predict ---
import requests

FASTAPI_URL = "http://ubuntu-ml-1:8001"  # Adjust if needed

# Cache predictors as singletons to avoid reloading on every request
_price_predictor = None
_demand_predictor = None
_yield_predictor = None


def get_price_predictor():
    global _price_predictor
    if _price_predictor is None:
        logger.info("Initializing Price Predictor (singleton)...")
        _price_predictor = PricePredictor()
    return _price_predictor


def get_demand_predictor():
    global _demand_predictor
    if _demand_predictor is None:
        logger.info("Initializing Demand Predictor (singleton)...")
        _demand_predictor = DemandPredictor()
        # If your DemandPredictor supports .load() (from the code I gave), load it once
        if hasattr(_demand_predictor, "load"):
            _demand_predictor.load()
    return _demand_predictor


def get_yield_predictor():
    global _yield_predictor
    if _yield_predictor is None:
        logger.info("Initializing Yield Predictor (singleton)...")
        _yield_predictor = YieldPredictor()
    return _yield_predictor


class PredictionHistoryViewSet(viewsets.ModelViewSet):
    """ViewSet for prediction history."""

    queryset = PredictionHistory.objects.all()
    serializer_class = PredictionHistorySerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"])
    def by_type(self, request):
        pred_type = request.query_params.get("type")
        if not pred_type:
            return Response({"error": "type parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        predictions = self.queryset.filter(prediction_type=pred_type)
        serializer = self.get_serializer(predictions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_crop(self, request):
        crop_name = request.query_params.get("crop")
        if not crop_name:
            return Response({"error": "crop parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        predictions = self.queryset.filter(crop_name__icontains=crop_name)
        serializer = self.get_serializer(predictions, many=True)
        return Response(serializer.data)


class ModelMetadataViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for model metadata."""

    queryset = ModelMetadata.objects.filter(is_active=True)
    serializer_class = ModelMetadataSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"])
    def active_models(self, request):
        models = self.queryset.all()
        serializer = self.get_serializer(models, many=True)
        return Response(serializer.data)


@api_view(["POST"])
@permission_classes([AllowAny])
def yield_predict(request):
    """Proxy crop yield prediction to FastAPI ML service."""
    try:
        fastapi_response = requests.post(
            f"{FASTAPI_URL}/yield/predict",
            json=request.data,
            timeout=10
        )
        return Response(fastapi_response.json(), status=fastapi_response.status_code)
    except requests.RequestException as e:
        return Response({"error": f"Proxy to FastAPI failed: {str(e)}"}, status=status.HTTP_502_BAD_GATEWAY)


@api_view(["POST"])
@permission_classes([AllowAny])
def price_predict(request):
    """Proxy crop price prediction to FastAPI ML service."""
    try:
        fastapi_response = requests.post(
            f"{FASTAPI_URL}/price/predict",
            json=request.data,
            timeout=10
        )
        return Response(fastapi_response.json(), status=fastapi_response.status_code)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)



# NEW: Demand Forecast API

@api_view(["POST"])
@permission_classes([AllowAny])
def demand_forecast(request):
    """Proxy demand forecast to FastAPI ML service."""
    try:
        fastapi_response = requests.post(
            f"{FASTAPI_URL}/demand/forecast",
            json=request.data,
            timeout=10
        )
        return Response(fastapi_response.json(), status=fastapi_response.status_code)
    except requests.RequestException as e:
        return Response({"error": f"Proxy to FastAPI failed: {str(e)}"}, status=status.HTTP_502_BAD_GATEWAY)


# Keep your old demand_predict endpoint for compatibility (optional)
@api_view(["POST"])
@permission_classes([AllowAny])
def demand_predict(request):
    """
    Old endpoint (single-value style).
    If your frontend uses it, keep it.
    Otherwise, you can remove it later.
    """
    serializer = DemandPredictionRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        predictor = get_demand_predictor()
        features: dict = serializer.validated_data # type: ignore
        crop_type = str(features.get("crop_type", ""))

        # If your predictor still supports predict(), use it
        if hasattr(predictor, "predict"):
            predict_fn = getattr(predictor, "predict")
            prediction = predict_fn(features)
            accuracy = getattr(predictor, "get_accuracy", lambda: {})()

            return Response(
                {
                    "prediction_type": "demand",
                    "crop_type": crop_type,
                    "predicted_demand": prediction,
                    "unit": "metric tons",
                    "confidence": accuracy.get("r2_score", 0.0),
                    "model_accuracy": {
                        "r2_score": accuracy.get("r2_score", 0.0),
                        "mae": accuracy.get("mae", 0.0),
                        "rmse": accuracy.get("rmse", 0.0),
                    },
                }
            )

        # Fallback for newer predictor implementations that only expose forecast_days()
        if hasattr(predictor, "forecast_days"):
            excel_path = os.path.join(settings.BASE_DIR, "data", "demand_dataset.xlsx")
            if not os.path.exists(excel_path):
                return Response(
                    {"error": f"Demand dataset not found at: {excel_path}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            df = pd.read_excel(excel_path)
            forecast_result = predictor.forecast_days(
                product_name=crop_type,
                forecast_days=20,
                consumption_trend=features.get("consumption_trend", "stable"),
                excel_df=df,
            )

            predicted_total = forecast_result.get("predicted_total_tonnes", 0)

            try:
                PredictionHistory.objects.create(
                    prediction_type="demand",
                    crop_name=crop_type,
                    input_features=features,
                    predicted_value=predicted_total,
                )
            except Exception:
                pass

            return Response(
                {
                    "prediction_type": "demand",
                    "crop_type": crop_type,
                    "predicted_demand": predicted_total,
                    "unit": forecast_result.get("unit", "tonnes"),
                    "confidence": 0.0,
                    "model_accuracy": {
                        "r2_score": 0.0,
                        "mae": 0.0,
                        "rmse": 0.0,
                    },
                }
            )

        return Response(
            {"error": "Demand predictor is missing both predict() and forecast_days()."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    except Exception as e:
        logger.error(f"Error in demand prediction: {str(e)}", exc_info=True)
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([AllowAny])
def price_forecast(request):
    """Proxy price forecast to FastAPI ML service."""
    try:
        fastapi_response = requests.post(
            f"{FASTAPI_URL}/price/forecast",
            json=request.data,
            timeout=10
        )
        return Response(fastapi_response.json(), status=fastapi_response.status_code)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)




@api_view(["POST"])
@permission_classes([AllowAny])
def prediction_explain(request):
    """Generate explanation for a prediction."""
    try:
        prediction_data = request.data
        prediction_type = prediction_data.get("prediction_type", "price")
        crop_type = prediction_data.get("crop_type", "unknown")
        predicted_value = prediction_data.get("predicted_value", 0)

        if prediction_type == "price":
            predictor = get_price_predictor()
        elif prediction_type == "yield":
            predictor = get_yield_predictor()
        elif prediction_type == "demand":
            predictor = get_demand_predictor()
        else:
            return Response({"error": "Invalid prediction type"}, status=status.HTTP_400_BAD_REQUEST)

        accuracy_data = getattr(predictor, "get_accuracy", lambda: {})()
        model_accuracy = accuracy_data.get("r2_score", 0.0)

        explanation = {
            "prediction_type": prediction_type,
            "crop_type": crop_type,
            "predicted_value": predicted_value,
            "factors": [],
            "model_info": {
                "algorithm": "Random Forest Regressor",
                "accuracy": model_accuracy,
                "features_used": len(getattr(predictor, "feature_columns", [])) or 0,
            },
        }

        # (keep your factors as-is; unchanged)
        if prediction_type == "price":
            explanation["factors"] = [
                {"name": "Seasonal Patterns", "importance": 0.40, "description": "Season affects supply and trends", "impact": "High"},
                {"name": "Supply & Demand Balance", "importance": 0.35, "description": "Market supply levels and demand", "impact": "High"},
                {"name": "Recent Price Trends", "importance": 0.15, "description": "Rolling averages and momentum", "impact": "Medium"},
                {"name": "Market Conditions", "importance": 0.10, "description": "Weather, transport, location", "impact": "Low"},
            ]
        elif prediction_type == "yield":
            explanation["factors"] = [
                {"name": "Soil Quality", "importance": 0.35, "description": "Soil nutrients and pH", "impact": "High"},
                {"name": "Weather Conditions", "importance": 0.30, "description": "Temp, rainfall, humidity", "impact": "High"},
                {"name": "Farming Practices", "importance": 0.20, "description": "Irrigation, fertilizer, pests", "impact": "Medium"},
                {"name": "Crop Variety", "importance": 0.15, "description": "Cultivar characteristics", "impact": "Medium"},
            ]
        else:
            explanation["factors"] = [
                {"name": "Consumer Preferences", "importance": 0.40, "description": "Historical consumption patterns", "impact": "High"},
                {"name": "Population Demographics", "importance": 0.25, "description": "Urban vs rural + income", "impact": "Medium"},
                {"name": "Price Sensitivity", "importance": 0.20, "description": "Demand elasticity", "impact": "Medium"},
                {"name": "Seasonal Factors", "importance": 0.15, "description": "Festivals + cultural preferences", "impact": "Low"},
            ]

        return Response(explanation)

    except Exception as e:
        logger.error(f"Error generating explanation: {str(e)}", exc_info=True)
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# keep your yield_forecast exactly if it already works in your project
@api_view(["POST"])
@permission_classes([AllowAny])
def yield_forecast(request):
    crop_type = request.data.get("crop_type")
    months = request.data.get("months", 6)

    if not crop_type:
        return Response({"error": "crop_type is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        months = int(months)
    except Exception:
        return Response({"error": "months must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

    if months < 1 or months > 24:
        return Response({"error": "months must be between 1 and 24"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        predictor = get_yield_predictor()
        series = predictor.forecast(crop_type=crop_type, months=months)

        try:
            PredictionHistory.objects.create(
                prediction_type="yield_forecast",
                crop_name=crop_type,
                input_features={"months": months},
                predicted_value=series[-1]["predicted_yield"] if series else 0,
            )
        except Exception:
            pass

        return Response(
            {
                "prediction_type": "yield_forecast",
                "crop_type": crop_type,
                "months": months,
                "unit": "kg/hectare",
                "series": series,
            }
        )

    except Exception as e:
        logger.error(f"Error in yield forecast: {str(e)}", exc_info=True)
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FloodPredictionView(APIView):
    """
    Flood Risk Prediction API
    
    Predicts flood risk for a given location based on weather, environmental,
    and infrastructure features.
    """
    permission_classes = [AllowAny]
    
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
        Proxy flood risk prediction to FastAPI ML service.
        """
        try:
            fastapi_response = requests.post(
                f"{FASTAPI_URL}/flood/predict",
                json=request.data,
                timeout=10
            )
            return Response(fastapi_response.json(), status=fastapi_response.status_code)
        except requests.RequestException as e:
            return Response({
                'success': False,
                'message': 'Proxy to FastAPI failed',
                'error': str(e),
                'prediction': None
            }, status=status.HTTP_502_BAD_GATEWAY)


class BatchFloodPredictionView(APIView):
    """
    Batch Flood Risk Prediction API
    
    Predicts flood risk for multiple locations in a single request.
    """
    permission_classes = [AllowAny]
    
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
    permission_classes = [AllowAny]
    
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
    permission_classes = [AllowAny]
    
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
@permission_classes([AllowAny])
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
