from ml_models.predictors.demand_predictor import DemandPredictor

# Test demand predictor
predictor = DemandPredictor()

# Test with tomato
result = predictor.predict({'crop_type': 'tomato'})
print(f'Tomato demand prediction: {result:.0f} metric tons')

# Get accuracy metrics
accuracy = predictor.get_accuracy()
print(f'\nModel Accuracy:')
print(f'  R² Score: {accuracy["r2"]:.4f} ({accuracy["r2"]*100:.2f}%)')
print(f'  MAE: {accuracy["mae"]:.0f} MT')
print(f'  RMSE: {accuracy["rmse"]:.0f} MT')

# Test with other crops
for crop in ['carrot', 'bean', 'cabbage']:
    result = predictor.predict({'crop_type': crop})
    print(f'{crop.capitalize()} demand: {result:.0f} MT')
