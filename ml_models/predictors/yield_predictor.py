import joblib
from pathlib import Path
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

