
import joblib
from pathlib import Path
=======
"""
Crop Yield Prediction Module
Predicts crop yield based on historical data and environmental factors using Random Forest.
"""



import numpy as np

import pandas as pd

ART_DIR = Path("ml_models/models")

def get_season(month: int) -> int:
    return 0 if month in [10,11,12,1,2,3] else 1

_model = None
_le = None
_last = None

def _load():
    global _model, _le, _last
    if _model is None:
        _model = joblib.load(ART_DIR / "yield_rf.joblib")
        _le = joblib.load(ART_DIR / "yield_label_encoder.joblib")
        _last = joblib.load(ART_DIR / "yield_last.joblib")

def forecast_yield(crop_type: str, horizon_months: int):
    _load()

    if crop_type not in _last["last3"]:
        raise ValueError(f"Unknown crop_type: {crop_type}")

    lags = _last["last3"][crop_type]
    if len(lags) < 3:
        raise ValueError(f"Not enough history for {crop_type} (need 3 months).")

    last_dt = pd.to_datetime(_last["last_month"][crop_type], format="%Y-%m")
    start_dt = last_dt + pd.DateOffset(months=1)

    product_code = int(_le.transform([crop_type])[0])
    lag1, lag2, lag3 = lags[-1], lags[-2], lags[-3]

    preds = []
    for i in range(horizon_months):
        dt = start_dt + pd.DateOffset(months=i)
        X = [[dt.year, dt.month, get_season(dt.month), product_code, lag1, lag2, lag3]]
        yhat = float(_model.predict(X)[0])

        preds.append({
            "month_year": dt.strftime("%Y-%m"),
            "predicted_yield_ha": yhat
        })

        # shift lags (multi-step forecasting)
        lag3, lag2, lag1 = lag2, lag1, yhat

    return {
        "crop_type": crop_type,
        "horizon_months": horizon_months,
        "start_month": start_dt.strftime("%Y-%m"),
        "unit": "ha",
        "predictions": preds
    }

import joblib
from pathlib import Path
import pandas as pd





class YieldPredictor:
    def __init__(self):
        base = Path(__file__).resolve().parents[1]  # ml_models/
        model_dir = base / "models"


        self.model = joblib.load(model_dir / "yield_rf.joblib")
        self.le = joblib.load(model_dir / "yield_label_encoder.joblib")
        self.last = joblib.load(model_dir / "yield_last.joblib")

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


    def _season(self, month: int) -> int:
        return 0 if month in [10, 11, 12, 1, 2, 3] else 1

    def predict(self, features: dict):
        """
        Keep compatibility with existing /predict/yield/ endpoint.
        You can ignore extra fields; only use crop_type.
        """
        crop_type = features.get("crop_type")
        if not crop_type:
            raise ValueError("crop_type is required")

        # Predict 1-step (next month)
        series = self.forecast(crop_type=crop_type, months=1)
        return series[0]["predicted_yield"]

    def forecast(self, crop_type: str, months: int):
        """
        Used by /yield/forecast/ for chart
        Returns: list of {month: 'YYYY-MM', predicted_yield: float}
        """
        if crop_type not in self.last["last3"]:
            raise ValueError(f"Unknown crop_type: {crop_type}")

        lags = self.last["last3"][crop_type]
        if len(lags) < 3:
            raise ValueError(f"Not enough history for {crop_type} (need 3 months).")

        last_dt = pd.to_datetime(self.last["last_month"][crop_type], format="%Y-%m")
        start_dt = last_dt + pd.DateOffset(months=1)

        product_code = int(self.le.transform([crop_type])[0])
        lag1, lag2, lag3 = lags[-1], lags[-2], lags[-3]

        out = []
        for i in range(months):
            dt = start_dt + pd.DateOffset(months=i)

            X = [[dt.year, dt.month, self._season(dt.month), product_code, lag1, lag2, lag3]]
            yhat = float(self.model.predict(X)[0])

            out.append({
                "month": dt.strftime("%Y-%m"),
                "predicted_yield": yhat
            })

            # shift lags for multi-step prediction
            lag3, lag2, lag1 = lag2, lag1, yhat

        return out

