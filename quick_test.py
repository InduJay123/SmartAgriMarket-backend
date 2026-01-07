import requests
import json
import time

# Wait for server to be ready
print("Testing APIs...")

# Test price prediction
url = "http://127.0.0.1:8000/api/ml/predict/price/"
payload = {
    "crop_type": "Rice",
    "season": "Yala",
    "supply": 1000,
    "demand": 1200,
    "market_trend": "stable"
}

try:
    response = requests.post(url, json=payload, timeout=10)
    print(f"\nPrice API Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Price API Error: {e}")

# Test demand prediction
url = "http://127.0.0.1:8000/api/ml/predict/demand/"
payload = {
    "crop_type": "Rice",
    "season": "Yala",
    "historical_demand": 1000,
    "population": 22000000,
    "consumption_trend": "increasing"
}

try:
    response = requests.post(url, json=payload, timeout=10)
    print(f"\nDemand API Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Demand API Error: {e}")

print("\nDone!")
