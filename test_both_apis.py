"""Test both Price and Demand APIs"""
import requests

BASE_URL = 'http://127.0.0.1:8000/api/ml'

print("=" * 50)
print("Testing Price Prediction API")
print("=" * 50)

try:
    price_data = {
        'crop_type': 'Tomato',
        'season': 'northeast_monsoon',
        'supply': 1000,
        'demand': 1200,
        'market_trend': 'stable'
    }
    response = requests.post(f'{BASE_URL}/predict/price/', json=price_data, timeout=30)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Predicted Price: Rs. {result.get('predicted_price', 'N/A')}")
        print(f"Model Accuracy: {result.get('model_accuracy', {})}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 50)
print("Testing Demand Prediction API")
print("=" * 50)

try:
    demand_data = {
        'crop_type': 'Tomato',
        'season': 'northeast_monsoon',
        'historical_demand': 1200,
        'population': 22000000,
        'consumption_trend': 'stable'
    }
    response = requests.post(f'{BASE_URL}/predict/demand/', json=demand_data, timeout=30)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Predicted Demand: {result.get('predicted_demand', 'N/A')}")
        print(f"Model Accuracy: {result.get('model_accuracy', {})}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 50)
print("Done!")
print("=" * 50)
