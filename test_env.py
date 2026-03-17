import requests
import json
resp = requests.post("http://127.0.0.1:8000/api/ml/predict/yield/", json={})
print(resp.text)
