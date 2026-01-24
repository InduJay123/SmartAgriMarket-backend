"""
Demand Predictor - Predicts vegetable demand in metric tons
Uses vegetable_demand3.csv dataset with Random Forest Regressor
"""
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import pickle


class DemandPredictor:
    """Predict crop demand based on historical data."""
    
    def __init__(self):
        self.model = None
        self.label_encoder = None
        self.df = None
        self.accuracy_metrics = {}
        self.crop_mapping = {
            'tomato': 'Tomato',
            'tomatoes': 'Tomato',
            'carrot': 'Carrot',
            'carrots': 'Carrot',
            'bean': 'Bean',
            'beans': 'Bean',
            'cabbage': 'Cabbage',
            'capsicum': 'Capsicum',
            'pepper': 'Capsicum',
            'peppers': 'Capsicum',
            'beet': 'Beet',
            'pumpkin': 'Pumpkin',
            'cucumber': 'Cucumber',
            'okra': 'Okra',
            'brinjal': 'Brinjal',
            'eggplant': 'Brinjal'
        }
        self._load_or_train_model()
    
    def _load_or_train_model(self):
        """Load trained model or train a new one."""
        try:
            # Try to load existing model
            model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'demand_model.pkl')
            encoder_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'demand_encoder.pkl')
            
            if os.path.exists(model_path) and os.path.exists(encoder_path):
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                with open(encoder_path, 'rb') as f:
                    self.label_encoder = pickle.load(f)
            else:
                self._train_model()
        except Exception as e:
            print(f"Error loading model, training new one: {e}")
            self._train_model()
    
    def _train_model(self):
        """Train the demand prediction model."""
        # Load data
        data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'vegetable_demand3.csv')
        self.df = pd.read_csv(data_path)
        
        # Prepare data
        self.df["year_month"] = pd.to_datetime(self.df["year_month"])
        self.df = self.df.sort_values(["product_name", "year_month"])
        
        self.df["year"] = self.df["year_month"].dt.year
        self.df["month"] = self.df["year_month"].dt.month
        self.df["lag_1"] = self.df.groupby("product_name")["demand_mt"].shift(1)
        self.df.dropna(inplace=True)
        
        # Encode product names
        self.label_encoder = LabelEncoder()
        self.df["product_encoded"] = self.label_encoder.fit_transform(self.df["product_name"])
        
        # Prepare features and target
        X = self.df[["year", "month", "lag_1", "product_encoded"]]
        y = self.df["demand_mt"]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, shuffle=False, random_state=42
        )
        
        # Train model
        self.model = RandomForestRegressor(
            n_estimators=300,
            max_depth=15,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train, y_train)
        
        # Calculate accuracy metrics
        y_pred = self.model.predict(X_test)
        self.accuracy_metrics = {
            'rmse': float(np.sqrt(mean_squared_error(y_test, y_pred))),
            'mae': float(mean_absolute_error(y_test, y_pred)),
            'r2': float(r2_score(y_test, y_pred))
        }
        
        # Save model
        try:
            model_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
            os.makedirs(model_dir, exist_ok=True)
            
            with open(os.path.join(model_dir, 'demand_model.pkl'), 'wb') as f:
                pickle.dump(self.model, f)
            with open(os.path.join(model_dir, 'demand_encoder.pkl'), 'wb') as f:
                pickle.dump(self.label_encoder, f)
        except Exception as e:
            print(f"Could not save model: {e}")
    
    def predict(self, features):
        """
        Predict demand for a crop.
        
        Args:
            features (dict): Dictionary with keys:
                - crop_type: str (e.g., 'tomato', 'carrot')
                - year: int (optional, defaults to 2025)
                - month: int (optional, defaults to current + 1)
        
        Returns:
            float: Predicted demand in metric tons
        """
        if self.model is None:
            raise ValueError("Model not trained")
        
        # Get crop name
        crop_input = features.get('crop_type', '').lower()
        crop_name = self.crop_mapping.get(crop_input, crop_input.capitalize())
        
        # Check if crop is in our dataset
        if crop_name not in self.label_encoder.classes_:
            # Return average demand for unknown crops
            if self.df is not None:
                return float(self.df['demand_mt'].mean())
            return 30000.0  # Fallback value
        
        # Encode product
        product_code = self.label_encoder.transform([crop_name])[0]
        
        # Get last known demand for this product
        if self.df is None:
            self._load_or_train_model()
        
        last_demand = self.df[self.df["product_name"] == crop_name]["demand_mt"].iloc[-1]
        
        # Get year and month
        year = features.get('year', 2025)
        month = features.get('month', 10)
        
        # Create feature vector



        
        future = pd.DataFrame({
            "year": [year],
            "month": [month],
            "lag_1": [last_demand],
            "product_encoded": [product_code]
        })
        
        # Predict
        prediction = self.model.predict(future)[0]
        return float(prediction)
    
    def get_accuracy(self):
        """Get model accuracy metrics from actual training."""
        if not self.accuracy_metrics:
            # Re-train to get metrics if not available
            self._train_model()
        return {
            'r2_score': self.accuracy_metrics.get('r2', 0.0),
            'mae': self.accuracy_metrics.get('mae', 0.0),
            'rmse': self.accuracy_metrics.get('rmse', 0.0)
        }
