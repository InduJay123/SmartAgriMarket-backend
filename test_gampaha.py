import requests
import json
print(requests.post("http://localhost:8000/api/ml/flood/predict/", json={
    "district": "Gampaha",
    "rainfall": 0,
    "river_level": 2.4,
    "soil_moisture": 52,
    "temperature": 27.67,
    "humidity": 74,
    "elevation": 0,
    "drainage_quality": "Moderate",
    "historical_floods": True
}).json())
