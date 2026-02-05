import pandas as pd
import joblib
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = BASE_DIR / "data" / "vegetable_yield_master_jan2022_sep2025.xlsx"

ART_DIR = Path("ml_models/models")
ART_DIR.mkdir(parents=True, exist_ok=True)

def get_season(month: int) -> int:
    return 0 if month in [10, 11, 12, 1, 2, 3] else 1  # Maha=0, Yala=1

df = pd.read_excel(DATA_PATH)
df["Month_Year"] = pd.to_datetime(df["Month_Year"], format="%Y-%m")
df["Year"] = df["Month_Year"].dt.year
df["Month"] = df["Month_Year"].dt.month
df["Season"] = df["Month"].apply(get_season)

le = LabelEncoder()
df["Product_Code"] = le.fit_transform(df["Product_Name"])

df = df.sort_values(["Product_Name", "Month_Year"])
df["Yield_lag_1"] = df.groupby("Product_Name")["Yield_ha"].shift(1)
df["Yield_lag_2"] = df.groupby("Product_Name")["Yield_ha"].shift(2)
df["Yield_lag_3"] = df.groupby("Product_Name")["Yield_ha"].shift(3)

df = df.dropna()

FEATURES = ["Year","Month","Season","Product_Code","Yield_lag_1","Yield_lag_2","Yield_lag_3"]
X, y = df[FEATURES], df["Yield_ha"]

model = RandomForestRegressor(
    n_estimators=300, max_depth=12, min_samples_split=5, random_state=42, n_jobs=-1
)
model.fit(X, y)

# last 3 yields per crop (needed for forecasting)
last3 = df.sort_values(["Product_Name","Month_Year"]).groupby("Product_Name")["Yield_ha"].apply(lambda s: list(s.tail(3))).to_dict()
last_month = df.sort_values(["Product_Name","Month_Year"]).groupby("Product_Name").tail(1).set_index("Product_Name")["Month_Year"].dt.strftime("%Y-%m").to_dict()

joblib.dump(model, ART_DIR / "yield_rf.joblib")
joblib.dump(le, ART_DIR / "yield_label_encoder.joblib")
joblib.dump({"last3": last3, "last_month": last_month}, ART_DIR / "yield_last.joblib")

print("✅ Saved yield model artifacts in:", ART_DIR)
