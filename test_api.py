"""Test the ML API endpoint"""
import requests

url = 'http://127.0.0.1:8000/api/ml/predict/price/'

# Test different vegetables
vegetables = ['tomato', 'Carrot', 'beans', 'Cabbage', 'potato']

print("Testing API predictions for different vegetables:\n")

for veg in vegetables:
    data = {
        'crop_type': veg,
        'season': 'northeast_monsoon',
        'supply': 1000,
        'demand': 1200,
        'market_trend': 'stable'
    }
    try:
        response = requests.post(url, json=data)
        result = response.json()
        price = result.get('predicted_price', 'ERROR')
        if isinstance(price, (int, float)):
            print(f"{veg}: Rs. {price:.2f}")
        else:
            print(f"{veg}: {result}")
    except Exception as e:
        print(f'{veg}: Error - {e}')
