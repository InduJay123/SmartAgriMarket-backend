"""
Helper functions for ML models.
"""

import pickle
import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def save_model(model: Any, model_path: str) -> bool:
    """
    Save a model to disk using pickle.

    Args:
        model: Model object to save
        model_path: Path to save the model

    Returns:
        True if successful, False otherwise
    """
    try:
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        logger.info(f"Model saved to {model_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving model: {str(e)}")
        return False


def load_model(model_path: str) -> Any:
    """
    Load a model from disk.

    Args:
        model_path: Path to the saved model

    Returns:
        Loaded model object
    """
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        logger.info(f"Model loaded from {model_path}")
        return model
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise


def save_config(config: dict, config_path: str) -> bool:
    """
    Save configuration to JSON file.

    Args:
        config: Configuration dictionary
        config_path: Path to save the config

    Returns:
        True if successful, False otherwise
    """
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        logger.info(f"Config saved to {config_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving config: {str(e)}")
        return False


def load_config(config_path: str) -> dict:
    """
    Load configuration from JSON file.

    Args:
        config_path: Path to the config file

    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        logger.info(f"Config loaded from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Error loading config: {str(e)}")
        raise
