# ml_models/predictors/demand_predictor.py

import os
import joblib
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
import calendar

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # ml_models/
MODELS_DIR = os.path.join(BASE_DIR, "models")

MODEL_PATH = os.path.join(MODELS_DIR, "demand_model.pkl")
META_PATH = os.path.join(MODELS_DIR, "demand_model_meta.pkl")


def _season_code(month: int) -> int:
    if month in (12, 1, 2):
        return 0
    if month in (3, 4):
        return 1
    if month in (5, 6, 7, 8, 9):
        return 2
    return 3


TREND_MULTIPLIERS = {
    "stable": 1.00,
    "increasing": 1.05,
    "decreasing": 0.95,
    "seasonal peak": 1.10,
    "seasonal low": 0.90,
}


class DemandPredictor:
    def __init__(self):
        self.model = None
        self.meta = None

    def load(self):
        if not os.path.exists(MODEL_PATH) or not os.path.exists(META_PATH):
            raise FileNotFoundError(
                "Demand model not found. Train it first: ml_models/training/train_demand_model.py"
            )
        self.model = joblib.load(MODEL_PATH)
        self.meta = joblib.load(META_PATH)
        return self

    def _product_code(self, product_name: str) -> int:
        product_to_code = self.meta["product_to_code"]
        if product_name not in product_to_code:
            # fallback: map unknown product to closest behavior (0)
            return 0
        return int(product_to_code[product_name])

    def _get_last_history(self, excel_df: pd.DataFrame, product_name: str):
        """
        Returns last known rows for that product for lag features.
        """
        df = excel_df.copy()
        df["year_month"] = df["year_month"].astype(str)
        df["date"] = pd.to_datetime(df["year_month"] + "-01", errors="coerce")
        df = df.dropna(subset=["date", "product_name", "demand_mt"])
        df = df[df["product_name"] == product_name].sort_values("date")
        if len(df) < 4:
            raise ValueError(f"Not enough history for {product_name}. Need at least 4 months.")
        return df

    def forecast_days(
        self,
        product_name: str,
        forecast_days: int,
        consumption_trend: str,
        excel_df: pd.DataFrame,
        start_day: date | None = None,
    ):
        """
        Forecast daily demand for next N days using monthly model.
        """
        if self.model is None or self.meta is None:
            self.load()

        if start_day is None:
            start_day = date.today()

        trend_key = (consumption_trend or "stable").strip().lower()
        base_mult = TREND_MULTIPLIERS.get(trend_key, 1.00)

        hist = self._get_last_history(excel_df, product_name)

        # Build initial lags from last 3 months
        last_vals = hist["demand_mt"].tail(3).tolist()
        lag1, lag2, lag3 = last_vals[-1], last_vals[-2], last_vals[-3]
        roll3 = float(np.mean(last_vals))

        # We forecast month-by-month as needed to cover forecast_days
        results = []
        cur = start_day

        # helper to predict one month demand
        def predict_month(y: int, m: int, lag1, lag2, lag3, roll3):
            prod_code = self._product_code(product_name)
            season = _season_code(m)
            X = np.array([[prod_code, y, m, season, lag1, lag2, lag3, roll3]], dtype=float)
            pred = float(self.model.predict(X)[0])
            return max(pred, 0.0)

        # Generate daily points
        remaining = forecast_days
        while remaining > 0:
            y, m = cur.year, cur.month
            days_in_month = calendar.monthrange(y, m)[1]
            month_pred = predict_month(y, m, lag1, lag2, lag3, roll3)

            # Convert to daily baseline
            daily_base = month_pred / float(days_in_month)

            # Apply trend smoothly across horizon (slight ramp)
            # e.g. increasing: grows day by day a bit
            for i in range(days_in_month):
                if remaining <= 0:
                    break
                day = cur + timedelta(days=i)
                # ramp factor across requested range
                t = (forecast_days - remaining) / max(forecast_days - 1, 1)
                ramp = 1.0 + (base_mult - 1.0) * t
                demand_day = daily_base * ramp
                results.append({"date": day.isoformat(), "demand_tonnes": round(demand_day, 2)})
                remaining -= 1

            # Move to next month start
            # update lags using predicted month demand (recursive)
            lag3, lag2, lag1 = lag2, lag1, month_pred
            roll3 = float(np.mean([lag1, lag2, lag3]))

            # advance cur to first of next month
            if m == 12:
                cur = date(y + 1, 1, 1)
            else:
                cur = date(y, m + 1, 1)

        total = sum(x["demand_tonnes"] for x in results)
        return {
            "crop": product_name,
            "forecast_days": forecast_days,
            "unit": "tonnes",
            "consumption_trend": consumption_trend,
            "predicted_total_tonnes": round(total, 2),
            "data": results,
            "model": {
                "algorithm": "RandomForestRegressor",
                "trained_at": self.meta.get("trained_at"),
                "train_mae": self.meta.get("train_mae"),
            },
        }
