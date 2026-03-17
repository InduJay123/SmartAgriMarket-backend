import json
from ml_models.predictors.flood_predictor import get_predictor
features = {
    "district": "Kandy",
    "rainfall": 200,
    "river_level": 2,
    "soil_moisture": 70,
    "temperature": 25,
    "humidity": 90,
    "elevation": 4,
    "drainage_quality": "Moderate",
    "historical_floods": True
}
predictor = get_predictor()
result = predictor.predict(features)
print(json.dumps(result, indent=2))
