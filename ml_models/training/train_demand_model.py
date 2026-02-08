
import os
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # ml_models/
MODELS_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

MODEL_PATH = os.path.join(MODELS_DIR, "demand_model.pkl")
META_PATH = os.path.join(MODELS_DIR, "demand_model_meta.pkl")


def _season_code(month: int) -> int:
    # Sri Lanka seasons (roughly)
    # Northeast monsoon: Dec-Feb
    # First inter-monsoon: Mar-Apr
    # Southwest monsoon: May-Sep
    # Second inter-monsoon: Oct-Nov
    if month in (12, 1, 2):
        return 0
    if month in (3, 4):
        return 1
    if month in (5, 6, 7, 8, 9):
        return 2
    return 3  # 10,11


def make_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Parse year_month
    df["year_month"] = df["year_month"].astype(str)
    df["date"] = pd.to_datetime(df["year_month"] + "-01", errors="coerce")

    df = df.dropna(subset=["date", "product_name", "demand_mt"]).copy()
    df = df.sort_values(["product_name", "date"])

    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["season_code"] = df["month"].apply(_season_code)

    # Lag features per crop
    df["lag1"] = df.groupby("product_name")["demand_mt"].shift(1)
    df["lag2"] = df.groupby("product_name")["demand_mt"].shift(2)
    df["lag3"] = df.groupby("product_name")["demand_mt"].shift(3)

    # Rolling mean (previous 3 months)
    df["roll3"] = (
        df.groupby("product_name")["demand_mt"]
        .shift(1)
        .rolling(3, min_periods=1)
        .mean()
        .reset_index(level=0, drop=True)
    )

    # Drop rows where we don't have enough history
    df = df.dropna(subset=["lag1", "lag2", "lag3"]).copy()

    return df


def train_from_excel(excel_path: str) -> dict:
    raw = pd.read_excel(excel_path)

    needed = {"year_month", "product_name", "demand_mt"}
    if not needed.issubset(set(raw.columns)):
        raise ValueError(f"Excel must contain columns: {needed}. Found: {list(raw.columns)}")

    data = make_features(raw)

    # Encode product_name as integer codes
    products = sorted(data["product_name"].unique().tolist())
    product_to_code = {p: i for i, p in enumerate(products)}
    data["product_code"] = data["product_name"].map(product_to_code).astype(int)

    feature_cols = ["product_code", "year", "month", "season_code", "lag1", "lag2", "lag3", "roll3"]
    X = data[feature_cols].values
    y = data["demand_mt"].values

    model = RandomForestRegressor(
        n_estimators=400,
        random_state=42,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        n_jobs=-1,
    )
    model.fit(X, y)

    # quick sanity metric (train MAE)
    pred = model.predict(X)
    mae = float(mean_absolute_error(y, pred))

    joblib.dump(model, MODEL_PATH)
    meta = {
        "trained_at": datetime.utcnow().isoformat() + "Z",
        "feature_cols": feature_cols,
        "product_to_code": product_to_code,
        "train_mae": mae,
    }
    joblib.dump(meta, META_PATH)

    return {"model_path": MODEL_PATH, "meta_path": META_PATH, "train_mae": mae, "n_rows": int(len(data))}


if __name__ == "__main__":
    # Example usage:
    # python ml_models/training/train_demand_model.py "path/to/your.xlsx"
    import sys
    if len(sys.argv) < 2:
        print("Usage: python train_demand_model.py <excel_path>")
        sys.exit(1)
    result = train_from_excel(sys.argv[1])
    print(result)
