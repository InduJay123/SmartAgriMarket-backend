import requests
import json
print(requests.post("http://localhost:8000/api/ml/flood/predict/", json={
    "district": "Kalutara",
    "rainfall": 101,
    "river_level": 3.3,
    "soil_moisture": 66,
    "temperature": 26,
    "humidity": 76,
    "elevation": 0,
    "drainage_quality": "Moderate",
    "historical_floods": True
}).json())
