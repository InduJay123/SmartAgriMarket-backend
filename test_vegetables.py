"""Test different vegetables to verify different prices"""
import requests
import time

url = 'http://localhost:8000/api/ml/predict/price/'

vegetables = ['Tomato', 'Carrot', 'Beans', 'Cabbage', 'Potato']

print("=" * 50)
print("Testing Price Predictions for Different Vegetables")
print("=" * 50)

for veg in vegetables:
    data = {
        'crop_type': veg,
        'season': 'northeast_monsoon',
        'supply': 1000,
        'demand': 1200,
        'market_trend': 'stable'
    }
    try:
        response = requests.post(url, json=data, timeout=30)
        result = response.json()
        price = result.get('predicted_price', 'ERROR')
        print(f"{veg}: Rs. {price:.2f}" if isinstance(price, (int, float)) else f"{veg}: {result}")
    except requests.exceptions.ConnectionError:
        print(f"{veg}: ERROR - Cannot connect to server at {url}")
        print("Make sure the Django server is running!")
        break
    except Exception as e:
        print(f"{veg}: ERROR - {e}")

print("=" * 50)
