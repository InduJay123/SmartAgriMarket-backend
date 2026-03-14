"""
Configuration module for ML models.
"""

import os
from pathlib import Path


class Config:
    """Configuration settings for ML models."""

    # Paths
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    MODELS_DIR = BASE_DIR / 'ml_models' / 'models'
    DATA_DIR = BASE_DIR / 'data'
    RAW_DATA_DIR = DATA_DIR / 'raw'
    PROCESSED_DATA_DIR = DATA_DIR / 'processed'
    TRAINING_DATA_DIR = DATA_DIR / 'training'

    # Model settings
    RANDOM_STATE = 42
    TEST_SIZE = 0.2
    VALIDATION_SIZE = 0.1

    # Training parameters
    YIELD_MODEL_PARAMS = {
        'n_estimators': 100,
        'max_depth': 10,
        'random_state': RANDOM_STATE,
    }

    PRICE_MODEL_PARAMS = {
        'n_estimators': 100,
        'learning_rate': 0.1,
        'random_state': RANDOM_STATE,
    }

    DEMAND_MODEL_PARAMS = {
        'n_estimators': 100,
        'max_depth': 10,
        'random_state': RANDOM_STATE,
    }

    # Feature settings
    TEMPORAL_FEATURES = ['year', 'month', 'quarter', 'day_of_year']
    LAG_SIZES = [1, 7, 30]
    ROLLING_WINDOWS = [7, 14, 30]

    # Preprocessing
    OUTLIER_METHOD = 'iqr'
    MISSING_VALUE_STRATEGY = 'mean'
    NORMALIZATION_ENABLED = True

    @classmethod
    def create_directories(cls):
        """Create all necessary directories if they don't exist."""
        for directory in [
            cls.MODELS_DIR,
            cls.RAW_DATA_DIR,
            cls.PROCESSED_DATA_DIR,
            cls.TRAINING_DATA_DIR,
        ]:
            directory.mkdir(parents=True, exist_ok=True)
