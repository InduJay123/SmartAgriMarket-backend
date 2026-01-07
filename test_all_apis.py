"""Test all ML API endpoints"""
import requests

BASE_URL = 'http://127.0.0.1:8000/api/ml'

print("=" * 60)
print("Testing ML API Endpoints")
print("=" * 60)

# Test Price Prediction
print("\n1. PRICE PREDICTION:")
print("-" * 40)
price_data = {
    'crop_type': 'Tomato',
    'season': 'northeast_monsoon',
    'supply': 1000,
    'demand': 1200,
    'market_trend': 'stable'
}
try:
    response = requests.post(f'{BASE_URL}/predict/price/', json=price_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Predicted Price: Rs. {result.get('predicted_price', 'N/A'):.2f}")
        print(f"Model Accuracy: {result.get('model_accuracy', {})}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# Test Demand Prediction
print("\n2. DEMAND PREDICTION:")
print("-" * 40)
demand_data = {
    'crop_type': 'Tomato',
    'season': 'northeast_monsoon',
    'historical_demand': 1200,
    'population': 22000000,
    'consumption_trend': 'stable'
}
try:
    response = requests.post(f'{BASE_URL}/predict/demand/', json=demand_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Predicted Demand: {result.get('predicted_demand', 'N/A')}")
        print(f"Model Accuracy: {result.get('model_accuracy', {})}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# Test Yield Prediction
print("\n3. YIELD PREDICTION:")
print("-" * 40)
yield_data = {
    'crop_type': 'Tomato',
    'rainfall': 150,
    'temperature': 28,
    'soil_quality': 'good',
    'fertilizer': 50,
    'irrigation': True
}
try:
    response = requests.post(f'{BASE_URL}/predict/yield/', json=yield_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Predicted Yield: {result.get('predicted_yield', 'N/A')}")
        print(f"Model Accuracy: {result.get('model_accuracy', {})}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("All tests complete!")
print("=" * 60)
