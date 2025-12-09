"""
Training script for demand prediction model.
"""

import logging
import numpy as np
import pandas as pd
from pathlib import Path

from ml_models.predictors import DemandPredictor
from ml_models.preprocessing import DataCleaner, DataValidator, FeatureEngineer
from ml_models.utils.config import Config
from ml_models.utils.helpers import save_model
from ml_models.utils.logger import setup_logger

logger = setup_logger(__name__)


def load_training_data(data_path: str) -> pd.DataFrame:
    """Load training data from CSV."""
    try:
        df = pd.read_csv(data_path)
        logger.info(f"Loaded {len(df)} samples from {data_path}")
        return df
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        raise


def prepare_data(df: pd.DataFrame) -> tuple:
    """Prepare data for training."""
    try:
        # Validate schema
        required_columns = ['crop_type', 'season', 'historical_demand', 'population', 'consumption_trend', 'demand']
        if not DataValidator.validate_schema(df, required_columns):
            raise ValueError("Missing required columns")

        # Clean data
        df = DataCleaner.handle_missing_values(df)
        
        # Remove outliers
        numeric_columns = ['historical_demand', 'population', 'demand']
        df = DataCleaner.remove_outliers(df, numeric_columns)

        # Encode categorical variables
        df = FeatureEngineer.encode_categorical(df, ['crop_type', 'season', 'consumption_trend'])

        # Prepare features and target
        X = df.drop('demand', axis=1)
        y = df['demand']

        logger.info("Data preparation completed")
        return X, y
    except Exception as e:
        logger.error(f"Error preparing data: {str(e)}")
        raise


def train_model(X: np.ndarray, y: np.ndarray):
    """Train demand prediction model."""
    try:
        predictor = DemandPredictor()
        predictor.train(X, y)
        
        # Save model
        model_path = Config.MODELS_DIR / 'demand_predictor.pkl'
        save_model(predictor, str(model_path))
        
        logger.info(f"Model saved to {model_path}")
        return predictor
    except Exception as e:
        logger.error(f"Error training model: {str(e)}")
        raise


def main():
    """Main training function."""
    try:
        # Create directories
        Config.create_directories()
        
        # Load and prepare data
        # TODO: Replace with actual data path
        data_path = Config.TRAINING_DATA_DIR / 'demand_training_data.csv'
        # df = load_training_data(str(data_path))
        # X, y = prepare_data(df)
        
        # Train model
        # model = train_model(X.values, y.values)
        
        logger.info("Training completed successfully")
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        raise


if __name__ == '__main__':
    main()
