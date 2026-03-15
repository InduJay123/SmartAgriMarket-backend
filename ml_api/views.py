"""
Views for ML API.
"""

import os
import pandas as pd
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

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
def yield_predict(request):
    """Predict crop yield."""
    serializer = YieldPredictionRequestSerializer(data=request.data)
    if not serializer.is_valid():
        logger.error(f"Yield prediction validation error: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        predictor = get_yield_predictor()
        features = serializer.validated_data
        prediction = predictor.predict(features)

        accuracy = predictor.get_accuracy() if hasattr(predictor, "get_accuracy") else {}

        try:
            PredictionHistory.objects.create(
                prediction_type="yield",
                crop_name=features["crop_type"],
                input_features=features,
                predicted_value=prediction,
            )
        except Exception:
            pass

        return Response(
            {
                "prediction_type": "yield",
                "crop_type": features["crop_type"],
                "predicted_yield": prediction,
                "unit": "kg/hectare",
                "confidence": accuracy.get("r2", accuracy.get("r2_score", 0.88)),
                "model_accuracy": {
                    "r2_score": accuracy.get("r2", accuracy.get("r2_score", 0.88)),
                    "mae": accuracy.get("mae", 250),
                    "rmse": accuracy.get("rmse", 380),
                },
            }
        )
    except Exception as e:
        logger.error(f"Error in yield prediction: {str(e)}", exc_info=True)
        return Response({"error": f"Yield prediction failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def price_predict(request):
    """Predict crop price."""
    serializer = PricePredictionRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        predictor = get_price_predictor()
        features = serializer.validated_data

        crop_type = features["crop_type"]
        prediction_features = {
            "product": crop_type,
            "date": features.get("date", timezone.now()),
        }

        prediction = predictor.predict(prediction_features)
        accuracy = predictor.get_accuracy() if hasattr(predictor, "get_accuracy") else {}

        try:
            PredictionHistory.objects.create(
                prediction_type="price",
                crop_name=crop_type,
                input_features=features,
                predicted_value=prediction,
            )
        except Exception:
            pass

        return Response(
            {
                "prediction_type": "price",
                "crop_type": crop_type,
                "predicted_price": prediction,
                "currency": "LKR",
                "confidence": accuracy.get("r2_score", 0.0),
                "model_accuracy": {
                    "r2_score": accuracy.get("r2_score", 0.0),
                    "mae": accuracy.get("mae", 0.0),
                    "rmse": accuracy.get("rmse", 0.0),
                },
            }
        )
    except Exception as e:
        logger.error(f"Error in price prediction: {str(e)}", exc_info=True)
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# NEW: Demand Forecast API

@api_view(["POST"])
def demand_forecast(request):
    """
    Forecast DAILY demand for next N days.
    Expected payload:
      {
        "crop_type": "Cabbage",
        "forecast_days": 20,
        "consumption_trend": "Stable"
      }
    """
    crop_type = request.data.get("crop_type") or request.data.get("crop")
    forecast_days = request.data.get("forecast_days", 20)
    consumption_trend = request.data.get("consumption_trend", "Stable")

    if not crop_type:
        return Response({"error": "crop_type is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        forecast_days = int(forecast_days)
    except Exception:
        return Response({"error": "forecast_days must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

    # your UI slider is 3..30
    if forecast_days < 3 or forecast_days > 30:
        return Response({"error": "forecast_days must be between 3 and 30"}, status=status.HTTP_400_BAD_REQUEST)

    # Excel dataset path (put your file here)
    excel_path = os.path.join(settings.BASE_DIR, "data", "demand_dataset.xlsx")
    if not os.path.exists(excel_path):
        return Response(
            {"error": f"Demand dataset not found at: {excel_path}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    try:
        df = pd.read_excel(excel_path)

        predictor = get_demand_predictor()

        # IMPORTANT: This requires your DemandPredictor to have forecast_days(...)
        if not hasattr(predictor, "forecast_days"):
            return Response(
                {"error": "Your DemandPredictor does not have forecast_days(). Please add it."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        result = predictor.forecast_days(
            product_name=crop_type,
            forecast_days=forecast_days,
            consumption_trend=consumption_trend,
            excel_df=df,
        )

        # Save history (optional)
        try:
            PredictionHistory.objects.create(
                prediction_type="demand_forecast",
                crop_name=crop_type,
                input_features={
                    "forecast_days": forecast_days,
                    "consumption_trend": consumption_trend,
                },
                predicted_value=result.get("predicted_total_tonnes", 0),
            )
        except Exception:
            pass

        return Response(result, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error in demand forecast: {str(e)}", exc_info=True)
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Keep your old demand_predict endpoint for compatibility (optional)
@api_view(["POST"])
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
        features = serializer.validated_data

        # If your predictor still supports predict(), use it
        if hasattr(predictor, "predict"):
            prediction = predictor.predict(features)
            accuracy = predictor.get_accuracy() if hasattr(predictor, "get_accuracy") else {}

            return Response(
                {
                    "prediction_type": "demand",
                    "crop_type": features.get("crop_type"),
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

        return Response(
            {"error": "DemandPredictor.predict() not found. Use /demand/forecast/ instead."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    except Exception as e:
        logger.error(f"Error in demand prediction: {str(e)}", exc_info=True)
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def price_forecast(request):
    """
    Forecast DAILY price for next N days.
    Expected payload:
      {
        "crop_type": "Tomato",
        "forecast_days": 30
      }
    """
    crop_type = request.data.get("crop_type") or request.data.get("crop")
    forecast_days = request.data.get("forecast_days", 30)

    if not crop_type:
        return Response({"error": "crop_type is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        forecast_days = int(forecast_days)
    except Exception:
        return Response({"error": "forecast_days must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

    if forecast_days < 1 or forecast_days > 30:
        return Response({"error": "forecast_days must be between 1 and 30"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        predictor = get_price_predictor()

        # use your existing predict_future() from PricePredictor
        series = predictor.predict_future(
            product=crop_type,
            days_ahead=forecast_days,
            start_date=timezone.now()
        )

        if not series:
            return Response({"error": "No forecast data available"}, status=status.HTTP_404_NOT_FOUND)

        prices = [item["predicted_price"] for item in series]
        today_price = prices[0] if prices else 0
        avg_price = round(sum(prices) / len(prices), 2) if prices else 0

        try:
            PredictionHistory.objects.create(
                prediction_type="price_forecast",
                crop_name=crop_type,
                input_features={"forecast_days": forecast_days},
                predicted_value=today_price,
            )
        except Exception:
            pass

        return Response(
            {
                "prediction_type": "price_forecast",
                "crop_type": crop_type,
                "forecast_days": forecast_days,
                "currency": "LKR",
                "today_price": round(today_price, 2),   # Premium Price
                "avg_30_days": avg_price,               # Market Average
                "series": series                        # full 30-day list
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.error(f"Error in price forecast: {str(e)}", exc_info=True)
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(["POST"])
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

        accuracy_data = predictor.get_accuracy() if hasattr(predictor, "get_accuracy") else {}
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
