# Machine Learning Module - SmartAgriMarket Backend

This directory contains all machine learning models, predictors, and APIs for crop forecasting and prediction.

## Structure Overview

```
ml_models/
├── predictors/           # ML prediction engines
│   ├── yield_predictor.py       # Crop yield predictions
│   ├── price_predictor.py       # Price forecasting
│   └── demand_predictor.py      # Demand predictions
├── preprocessing/        # Data preparation utilities
│   ├── data_cleaner.py          # Missing values, outliers handling
│   ├── feature_engineering.py   # Feature creation and transformation
│   └── data_validator.py        # Data quality validation
├── training/            # Model training scripts
│   ├── train_yield_model.py
│   ├── train_price_model.py
│   └── train_demand_model.py
├── utils/               # Utility functions
│   ├── config.py                # Configuration settings
│   ├── logger.py                # Logging setup
│   └── helpers.py               # Helper functions
├── tests/               # Unit tests
└── models/              # Trained model files (pickled)

ml_api/                 # Django REST API for ML predictions
├── models.py            # PredictionHistory, ModelMetadata
├── serializers.py       # Request/response serializers
├── views.py             # API views
├── urls.py              # URL routing
└── admin.py             # Django admin interface

data/                   # Data storage
├── raw/                 # Original, unprocessed data
├── processed/           # Cleaned data ready for training
└── training/            # Training datasets

notebooks/              # Jupyter notebooks
├── eda.ipynb            # Exploratory Data Analysis
├── model_training.ipynb
└── model_evaluation.ipynb
```

## Getting Started

### 1. Install ML Dependencies

```bash
pip install -r requirements-ml.txt
```

### 2. Configure Django

The `ml_api` app is already configured in `smartagri_backend/settings.py`:

```python
INSTALLED_APPS = [
    ...
    'ml_api',
]
```

### 3. Run Migrations

```bash
python manage.py makemigrations ml_api
python manage.py migrate ml_api
```

### 4. Use the Predictors

#### Yield Prediction
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
```

#### Price Prediction
```python
from ml_models.predictors import PricePredictor

predictor = PricePredictor()
features = {
    'crop_type': 'rice',
    'season': 'monsoon',
    'supply': 1000,
    'demand': 900,
    'market_trend': 'stable'
}
prediction = predictor.predict(features)
```

#### Demand Prediction
```python
from ml_models.predictors import DemandPredictor

predictor = DemandPredictor()
features = {
    'crop_type': 'rice',
    'season': 'monsoon',
    'historical_demand': 1000,
    'population': 5000000,
    'consumption_trend': 'increasing'
}
prediction = predictor.predict(features)
```

## API Endpoints

### Prediction Endpoints

**POST** `/api/ml/predict/yield/`
- Request: Yield prediction features
- Response: Predicted yield value

**POST** `/api/ml/predict/price/`
- Request: Price prediction features
- Response: Predicted price

**POST** `/api/ml/predict/demand/`
- Request: Demand prediction features
- Response: Predicted demand

### Model Management Endpoints

**GET** `/api/ml/models/`
- Get all active models with metadata

**GET** `/api/ml/models/active_models/`
- Get only active models

### Prediction History Endpoints

**GET** `/api/ml/history/`
- Get all predictions

**GET** `/api/ml/history/by_type/?type=yield`
- Filter predictions by type (yield/price/demand)

**GET** `/api/ml/history/by_crop/?crop=rice`
- Filter predictions by crop name

## Training Models

### Training a Yield Model

```bash
python ml_models/training/train_yield_model.py
```

The training script:
1. Loads data from `data/training/yield_training_data.csv`
2. Validates and cleans the data
3. Removes outliers
4. Engineers features
5. Trains the model
6. Saves to `ml_models/models/yield_predictor.pkl`

### Data Format

Training data should be CSV with required columns:

**Yield Training Data:**
```csv
crop_type,rainfall,temperature,soil_quality,fertilizer,irrigation,yield
rice,1200,28.5,good,50,true,5000
wheat,800,20,fair,40,false,3500
...
```

**Price Training Data:**
```csv
crop_type,season,supply,demand,market_trend,price
rice,monsoon,1000,900,stable,2500
wheat,summer,800,850,increasing,3000
...
```

**Demand Training Data:**
```csv
crop_type,season,historical_demand,population,consumption_trend,demand
rice,monsoon,1000,5000000,stable,950
wheat,summer,800,5000000,increasing,850
...
```

## Data Preprocessing

### DataCleaner
- `handle_missing_values()`: Fill missing values with mean/median or drop
- `remove_outliers()`: Use IQR or Z-score method
- `normalize_data()`: Normalize to 0-1 range

### FeatureEngineer
- `create_temporal_features()`: Extract year, month, quarter, etc.
- `create_lag_features()`: Create lagged features for time series
- `create_rolling_features()`: Create rolling window features
- `encode_categorical()`: Label encode categorical variables

### DataValidator
- `check_data_quality()`: Get quality metrics
- `validate_schema()`: Check for required columns
- `validate_value_ranges()`: Ensure values are within expected ranges

## Configuration

Edit `ml_models/utils/config.py` to customize:
- Model parameters
- Feature settings
- Preprocessing strategies
- Paths for models and data

## Testing

Run the test suite:

```bash
python -m pytest ml_models/tests/
```

Or with Django:

```bash
python manage.py test ml_api
```

## Logging

Logs are automatically created in:
```
logs/
├── ml_models.log
├── ml_api.log
└── ml_models.training.log
```

## Next Steps

1. **Prepare Training Data**: Place CSV files in `data/training/`
2. **Train Models**: Run training scripts to create models
3. **API Testing**: Test endpoints using Postman or curl
4. **Model Evaluation**: Use notebooks to evaluate model performance
5. **Production Deployment**: Follow Django deployment guidelines

## Common Issues

### "No module named 'scikit-learn'"
Install ML dependencies:
```bash
pip install -r requirements-ml.txt
```

### Model not found error
Ensure models are trained first:
```bash
python ml_models/training/train_yield_model.py
```

### Migration errors
Run migrations:
```bash
python manage.py migrate ml_api
```

## References

- [scikit-learn Documentation](https://scikit-learn.org/)
- [Pandas Documentation](https://pandas.pydata.org/)
- [Django REST Framework](https://www.django-rest-framework.org/)
