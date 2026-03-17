import requests
import json
try:
    resp = requests.post("http://127.0.0.1:8000/api/ml/flood/predict/", json={
        "district": "Gampaha",
        "rainfall": 0,
        "river_level": 2.4,
        "soil_moisture": 52,
        "temperature": 27.67,
        "humidity": 74,
        "elevation": 0,
        "drainage_quality": "Moderate",
        "historical_floods": True
    })
    print(resp.status_code)
    print(resp.json())
except Exception as e:
    print("Error:", e)
