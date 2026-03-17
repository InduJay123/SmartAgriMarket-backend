from ml_models.predictors.flood_predictor import get_predictor
predictor = get_predictor()
features = {
    "district": "Gampaha",
    "rainfall": 0,
    "river_level": 2.4,
    "soil_moisture": 52,
    "temperature": 27.67,
    "humidity": 74,
    "elevation": 0,
    "drainage_quality": "Moderate",
    "historical_floods": True
}
print(predictor.predict(features))
