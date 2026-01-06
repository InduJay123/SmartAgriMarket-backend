import pandas as pd
import numpy as np

df = pd.read_csv("vegetable_demand3.csv")
df.head()
df.shape

df["year_month"] = pd.to_datetime(df["year_month"])
df = df.sort_values(["product_name", "year_month"])

df["year"] = df["year_month"].dt.year
df["month"] = df["year_month"].dt.month
df["lag_1"] = df.groupby("product_name")["demand_mt"].shift(1)
df.dropna(inplace=True)
df.head()

from sklearn.preprocessing import LabelEncoder

le = LabelEncoder()
df["product_encoded"] = le.fit_transform(df["product_name"])

X = df[["year", "month", "lag_1", "product_encoded"]]
y = df["demand_mt"]

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    shuffle=False
)

from sklearn.ensemble import RandomForestRegressor

model = RandomForestRegressor(
    n_estimators=300,
    max_depth=15,
    random_state=42
)

model.fit(X_train, y_train)

from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

y_pred = model.predict(X_test)

rmse = np.sqrt(mean_squared_error(y_test, y_pred))
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

rmse, mae, r2


import matplotlib.pyplot as plt

plt.figure()
plt.plot(y_test.values, label="Actual")
plt.plot(y_pred, label="Predicted")
plt.legend()
plt.title("Actual vs Predicted Demand")
plt.show()


product = "Bean"
product_code = le.transform([product])[0]

last_demand = df[df["product_name"] == product]["demand_mt"].iloc[-1]

future = pd.DataFrame({
    "year": [2025],
    "month": [10],
    "lag_1": [last_demand],
    "product_encoded": [product_code]
})

model.predict(future)
