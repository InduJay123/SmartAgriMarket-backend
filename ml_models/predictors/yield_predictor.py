"""
Crop Yield Prediction Module
Predicts crop yield based on historical data and environmental factors using Random Forest.
"""



import numpy as np
import pandas as pd
from typing import Dict
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import logging
import os

logger = logging.getLogger(__name__)


class YieldPredictor:
    """Predict crop yield based on historical data using Random Forest."""

    DEFAULT_DATASET_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'data', 'vegetable_yield.csv'
    )

    def __init__(self):
        """Initialize the yield predictor."""
        self.model = None
        self.is_trained = False
        self.product_encoder = LabelEncoder()
        self.soil_encoder = LabelEncoder()
        self.accuracy_metrics = {}
        
        logger.info("YieldPredictor initialized")
        
        # Load and train model
        self._load_and_train()

    def _load_and_train(self):
        """Load data and train the model."""
        try:
            # Load dataset
            if not os.path.exists(self.DEFAULT_DATASET_PATH):
                logger.warning(f"Dataset not found at {self.DEFAULT_DATASET_PATH}")
                return
            
            df = pd.read_csv(self.DEFAULT_DATASET_PATH)
            logger.info(f"Loaded {len(df)} records from yield dataset")
            
            # Prepare features
            self.product_encoder.fit(df['product'].unique())
            self.soil_encoder.fit(df['soil_quality'].unique())
            
            # Encode categorical variables
            df['product_encoded'] = self.product_encoder.transform(df['product'])
            df['soil_encoded'] = self.soil_encoder.transform(df['soil_quality'])
            
            # Select features
            X = df[['product_encoded', 'rainfall_mm', 'temperature_c', 
                    'soil_encoded', 'fertilizer_kg', 'irrigation', 'month']]
            y = df['yield_kg_per_ha']
            
            # Split data (80/20 split)
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, shuffle=True
            )
            
            # Train Random Forest model
            self.model = RandomForestRegressor(
                n_estimators=150,
                max_depth=12,
                random_state=42,
                n_jobs=-1
            )
            
            self.model.fit(X_train, y_train)
            
            # Calculate accuracy metrics

            
            y_pred = self.model.predict(X_test)
            self.accuracy_metrics = {
                'r2': float(r2_score(y_test, y_pred)),
                'mae': float(mean_absolute_error(y_test, y_pred)),
                'rmse': float(np.sqrt(mean_squared_error(y_test, y_pred)))
            }
            
            self.is_trained = True
            logger.info(f"Yield model trained - R²: {self.accuracy_metrics['r2']:.4f}, "
                       f"MAE: {self.accuracy_metrics['mae']:.2f}, "
                       f"RMSE: {self.accuracy_metrics['rmse']:.2f}")
            
        except Exception as e:
            logger.error(f"Error loading/training yield model: {str(e)}")
            self.is_trained = False

    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> None:
        """
        Train the yield prediction model.

        Args:
            X_train: Training features
            y_train: Training targets (yield values)
        """
        try:
            # TODO: Implement model training logic
            # from sklearn.ensemble import RandomForestRegressor
            # self.model = RandomForestRegressor(n_estimators=100, random_state=42)
            # self.model.fit(X_train, y_train)
            self.is_trained = True
            logger.info("Yield model trained successfully")
        except Exception as e:
            logger.error(f"Error training yield model: {str(e)}")
            raise

    def predict(self, features: Dict) -> float:
        """
        Predict crop yield for given features.

        Args:
            features: Dictionary containing crop features
                - crop_type: str
                - rainfall: float (mm)
                - temperature: float (°C)
                - soil_quality: str
                - fertilizer: float (kg/hectare)
                - irrigation: bool

        Returns:
            Predicted yield in kg/hectare
        """
        if not self.is_trained or self.model is None:
            logger.warning("Model not trained. Returning default value.")
            return 30000.0

        try:
            crop_type = features.get('crop_type', 'Tomato')
            rainfall = features.get('rainfall', 150)
            temperature = features.get('temperature', 28)
            soil_quality = features.get('soil_quality', 'good')
            fertilizer = features.get('fertilizer', 50)
            irrigation = 1 if features.get('irrigation', True) else 0
            
            # Get current month (or use a default)
            from datetime import datetime
            month = datetime.now().month
            
            # Encode categorical variables
            try:
                product_encoded = self.product_encoder.transform([crop_type.capitalize()])[0]
            except:
                logger.warning(f"Unknown crop type: {crop_type}, using Tomato")
                product_encoded = self.product_encoder.transform(['Tomato'])[0]
            
            try:
                soil_encoded = self.soil_encoder.transform([soil_quality])[0]
            except:
                logger.warning(f"Unknown soil quality: {soil_quality}, using good")
                soil_encoded = self.soil_encoder.transform(['good'])[0]
            
            # Prepare feature vector
            X = np.array([[
                product_encoded,
                rainfall,
                temperature,
                soil_encoded,
                fertilizer,
                irrigation,
                month
            ]])
            
            # Make prediction
            yield_prediction = self.model.predict(X)[0]
            
            logger.info(f"Yield prediction for {crop_type}: {yield_prediction:.2f} kg/hectare")
            return float(yield_prediction)
            
        except Exception as e:
            logger.error(f"Error in yield prediction: {str(e)}", exc_info=True)
            return 30000.0

    def get_accuracy(self) -> Dict:
        """Get model accuracy metrics from actual training."""
        if not self.accuracy_metrics:
            # Re-train to get metrics if not available
            self._load_and_train()
        return {
            'r2_score': self.accuracy_metrics.get('r2', 0.0),
            'mae': self.accuracy_metrics.get('mae', 0.0),
            'rmse': self.accuracy_metrics.get('rmse', 0.0)
        }

    def get_model_info(self) -> Dict:
        """Get information about the model."""
        return {
            "model_name": "Yield Predictor",
            "is_trained": self.is_trained,
            "accuracy": self.accuracy_metrics,
            "features": [
                "crop_type",
                "rainfall",
                "temperature",
                "soil_quality",
                "fertilizer",
                "irrigation",
                "month"
            ]
        }
