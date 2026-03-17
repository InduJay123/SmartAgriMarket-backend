import requests
resp = requests.get("http://127.0.0.1:8000/api/ml/flood/model-info/")
print(resp.status_code)
print(resp.text)
