# ML Development Quick Start Guide

## Step 1: Set Up the Environment

```bash
# Activate your virtual environment
cd c:\Users\User\OneDrive\Documents\GitHub\SmartAgriMarket-backend
.\venv\Scripts\Activate.ps1

# Install ML dependencies
pip install -r requirements-ml.txt
```

## Step 2: Initialize the ML Module

```bash
# Create migrations for ml_api
python manage.py makemigrations ml_api

# Apply migrations
python manage.py migrate ml_api

# Create a superuser (if not already created)
python manage.py createsuperuser
```

## Step 3: Test the ML Module

```bash
# Run Django development server
python manage.py runserver

# In another terminal, test the API
curl http://localhost:8000/api/ml/models/
```

## Step 4: Prepare Training Data

Create CSV files in the `data/training/` directory:

### Example: yield_training_data.csv
```
crop_type,rainfall,temperature,soil_quality,fertilizer,irrigation,yield
rice,1200,28.5,good,50,true,5000
wheat,800,20,fair,40,false,3500
maize,1000,25,good,45,true,4500
```

## Step 5: Train a Model

```bash
# Train yield prediction model
python ml_models/training/train_yield_model.py

# Train price prediction model
python ml_models/training/train_price_model.py

# Train demand prediction model
python ml_models/training/train_demand_model.py
```

## Step 6: Use the API

### Via Python
```python
from ml_models.predictors import YieldPredictor

predictor = YieldPredictor()
features = {
    'crop_type': 'rice',
    'rainfall': 1200,
    'temperature': 28.5,
    'soil_quality': 'good',
    'fertilizer': 50,
    'irrigation': True
}
prediction = predictor.predict(features)
print(f"Predicted yield: {prediction} kg/hectare")
```

### Via REST API
```bash
curl -X POST http://localhost:8000/api/ml/predict/yield/ \
  -H "Content-Type: application/json" \
  -d '{
    "crop_type": "rice",
    "rainfall": 1200,
    "temperature": 28.5,
    "soil_quality": "good",
    "fertilizer": 50,
    "irrigation": true
  }'
```

## Step 7: Monitor Predictions

View prediction history in Django admin:
- Navigate to: http://localhost:8000/admin
- Login with your superuser credentials
- View "Prediction History" and "Model Metadata"

## Project Structure Reference

- **ml_models/predictors/**: Core prediction engines
- **ml_models/preprocessing/**: Data cleaning and feature engineering
- **ml_models/training/**: Model training scripts
- **ml_models/utils/**: Configuration and utilities
- **ml_api/**: Django REST API app
- **data/**: Training and raw data directories
- **notebooks/**: Jupyter notebooks for analysis

## Important Files

- `requirements-ml.txt`: ML dependencies
- `ML_README.md`: Detailed documentation
- `ml_models/utils/config.py`: Configuration settings
- `ml_models/predictors/yield_predictor.py`: Example predictor

## Next Steps

1. Add training data to `data/training/`
2. Implement actual ML models (replace TODO sections)
3. Train models using provided scripts
4. Test API endpoints
5. Integrate with frontend

## Troubleshooting

### Models not predicting
- Ensure models are trained first
- Check logs in `logs/` directory
- Verify training data format

### API errors
- Check Django migrations: `python manage.py showmigrations ml_api`
- Verify ml_api is in INSTALLED_APPS
- Review server logs

### Import errors
- Install all dependencies: `pip install -r requirements-ml.txt`
- Ensure virtual environment is activated

## Need Help?

Refer to:
- `ML_README.md` - Full documentation
- `ml_models/tests/` - Test examples
- `notebooks/` - Analysis examples
