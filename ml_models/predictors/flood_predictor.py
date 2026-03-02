"""
Flood Risk Prediction Module

This module provides a FloodPredictor class that uses a trained Random Forest model
to predict flood risk based on location, weather, and environmental features.
"""

import os
import json
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Union


class FloodPredictor:
    """
    Flood Risk Predictor using Random Forest model.
    
    This class loads the trained model and provides methods to predict
    flood risk for given locations and weather conditions.
    """
    
    def __init__(self, models_dir: Optional[str] = None):
        """
        Initialize the FloodPredictor with the trained model.
        
        Args:
            models_dir: Path to the directory containing model files.
                       If None, uses the default ml_models/models directory.
        """
        if models_dir is None:
            # Get the base directory (ml_models folder)
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            models_dir = os.path.join(base_dir, 'models')
        
        self.models_dir = models_dir
        self.model = None
        self.scaler = None
        self.label_encoders = None
        self.feature_info = None
        self.is_loaded = False
        
        # Load the model on initialization
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the trained model, scaler, and encoders."""
        try:
            # Try loading the flood predictor model first
            model_path = os.path.join(self.models_dir, 'flood_predictor_rf.joblib')
            if not os.path.exists(model_path):
                # Fall back to the alternative model file
                model_path = os.path.join(self.models_dir, 'random_forest_flood_model.pkl')
            
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found in {self.models_dir}")
            
            self.model = joblib.load(model_path)
            
            # Load scaler
            scaler_path = os.path.join(self.models_dir, 'feature_scaler.joblib')
            if not os.path.exists(scaler_path):
                scaler_path = os.path.join(self.models_dir, 'scaler.pkl')
            
            if os.path.exists(scaler_path):
                self.scaler = joblib.load(scaler_path)
            
            # Load label encoders
            encoders_path = os.path.join(self.models_dir, 'label_encoders.pkl')
            if os.path.exists(encoders_path):
                self.label_encoders = joblib.load(encoders_path)
            
            # Load feature info
            feature_info_path = os.path.join(self.models_dir, 'feature_info.json')
            if os.path.exists(feature_info_path):
                with open(feature_info_path, 'r') as f:
                    self.feature_info = json.load(f)
            
            self.is_loaded = True
            print(f"✓ Model loaded successfully from {model_path}")
            
        except Exception as e:
            self.is_loaded = False
            print(f"✗ Error loading model: {str(e)}")
            raise
    
    def predict(self, features: Union[Dict[str, Any], pd.DataFrame]) -> Dict[str, Any]:
        """
        Predict flood risk for given features.
        
        Args:
            features: Dictionary or DataFrame containing the input features.
                     Required features depend on the trained model.
        
        Returns:
            Dictionary containing:
                - flood_predicted: Boolean indicating flood prediction
                - flood_probability: Probability of flood (0-100%)
                - risk_level: Categorical risk level (Very Low to Very High)
                - confidence: Model confidence score
        """
        if not self.is_loaded:
            raise RuntimeError("Model is not loaded. Please check model files.")
        
        # Convert dict to DataFrame if necessary
        if isinstance(features, dict):
            features_df = pd.DataFrame([features])
        else:
            features_df = features.copy()
        
        # Process categorical features
        if self.label_encoders:
            for col, encoder in self.label_encoders.items():
                if col in features_df.columns:
                    try:
                        features_df[col] = encoder.transform(features_df[col].astype(str))
                    except ValueError:
                        # Handle unseen labels by using the most common class
                        features_df[col] = 0
        
        # Ensure all required features are present
        if self.feature_info and 'feature_names' in self.feature_info:
            required_features = self.feature_info['feature_names']
            missing_features = set(required_features) - set(features_df.columns)
            
            # Fill missing features with 0 (or median if we have it)
            for feature in missing_features:
                features_df[feature] = 0
            
            # Reorder columns to match training
            features_df = features_df[required_features]
        
        # Handle missing values
        features_df = features_df.fillna(0)
        
        # Scale features
        if self.scaler is not None:
            features_scaled = self.scaler.transform(features_df)
        else:
            features_scaled = features_df.values
        
        # Make prediction
        prediction = self.model.predict(features_scaled)[0]
        probability = self.model.predict_proba(features_scaled)[0]
        
        # Get flood probability (class 1)
        flood_prob = probability[1] * 100
        
        # Determine risk level
        risk_level = self._get_risk_level(flood_prob)
        
        return {
            'flood_predicted': bool(prediction),
            'flood_probability': round(flood_prob, 2),
            'risk_level': risk_level,
            'no_flood_probability': round(probability[0] * 100, 2),
            'confidence': round(max(probability) * 100, 2)
        }
    
    def predict_batch(self, features_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Predict flood risk for multiple locations.
        
        Args:
            features_list: List of feature dictionaries.
        
        Returns:
            List of prediction results.
        """
        return [self.predict(features) for features in features_list]
    
    def _get_risk_level(self, probability: float) -> str:
        """
        Convert flood probability to risk level category.
        
        Args:
            probability: Flood probability percentage (0-100).
        
        Returns:
            Risk level string.
        """
        if probability < 20:
            return 'Very Low'
        elif probability < 40:
            return 'Low'
        elif probability < 60:
            return 'Moderate'
        elif probability < 80:
            return 'High'
        else:
            return 'Very High'
    
    def get_feature_importance(self, top_n: int = 10) -> Dict[str, float]:
        """
        Get the top N most important features.
        
        Args:
            top_n: Number of top features to return.
        
        Returns:
            Dictionary of feature names and their importance scores.
        """
        if not self.is_loaded:
            raise RuntimeError("Model is not loaded.")
        
        if not hasattr(self.model, 'feature_importances_'):
            return {}
        
        if self.feature_info and 'feature_names' in self.feature_info:
            feature_names = self.feature_info['feature_names']
        else:
            feature_names = [f'feature_{i}' for i in range(len(self.model.feature_importances_))]
        
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return dict(zip(
            importance_df['feature'].head(top_n).tolist(),
            importance_df['importance'].head(top_n).round(4).tolist()
        ))
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model.
        
        Returns:
            Dictionary containing model information.
        """
        if not self.is_loaded:
            return {'status': 'not_loaded', 'error': 'Model not loaded'}
        
        info = {
            'status': 'loaded',
            'model_type': type(self.model).__name__,
            'has_scaler': self.scaler is not None,
            'has_encoders': self.label_encoders is not None,
            'has_feature_info': self.feature_info is not None,
        }
        
        if hasattr(self.model, 'n_estimators'):
            info['n_estimators'] = self.model.n_estimators
        
        if hasattr(self.model, 'max_depth'):
            info['max_depth'] = self.model.max_depth
        
        if self.feature_info:
            info['n_features'] = len(self.feature_info.get('feature_names', []))
        
        return info


# Singleton instance for API use
_predictor_instance: Optional[FloodPredictor] = None


def get_predictor() -> FloodPredictor:
    """
    Get or create the singleton FloodPredictor instance.
    
    Returns:
        FloodPredictor instance.
    """
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = FloodPredictor()
    return _predictor_instance
