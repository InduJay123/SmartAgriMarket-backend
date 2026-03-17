from ml_models.predictors.flood_predictor import get_predictor
features = {
    "district": "Kalutara",
    "rainfall": 101,
    "river_level": 3.3,
    "soil_moisture": 66,
    "temperature": 26,
    "humidity": 76,
    "elevation": 0,
    "drainage_quality": "Moderate",
    "historical_floods": True
}
predictor = get_predictor()
print(predictor.predict(features))
