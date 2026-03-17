import requests
import json
resp = requests.post("http://127.0.0.1:8000/api/ml/predict/yield/", json={
    "crop_type": "rice", "season": "Maha", "area_ha": 2
})
print(resp.status_code)
print(resp.text)
