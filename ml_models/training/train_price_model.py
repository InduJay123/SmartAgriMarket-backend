"""
Training script for crop price prediction model.
Uses the real vegetable_prices.csv dataset and PricePredictor class.
"""

import os
import sys
import logging

# Ensure project root is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml_models.predictors.price_predictor import PricePredictor
from ml_models.utils.config import Config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def main():
    """
    Train the price prediction model from vegetable_prices.csv and save
    the artifact to ml_models/models/price_predictor_model.pkl.
    """
    Config.create_directories()

    dataset_path = os.path.join(PROJECT_ROOT, "data", "vegetable_prices.csv")
    if not os.path.exists(dataset_path):
        logger.error(f"Dataset not found: {dataset_path}")
        sys.exit(1)

    logger.info(f"Training price model from {dataset_path}")

    predictor = PricePredictor(auto_train=False)

    metrics = predictor.train(
        filepath=dataset_path,
        target_column="Pettah_Wholesale",
        n_estimators=100,
        max_depth=None,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
    )

    logger.info("=== Training Results ===")
    logger.info(f"Train R²:  {metrics.get('train_r2', 0):.4f}")
    logger.info(f"Test  R²:  {metrics.get('test_r2', 0):.4f}")
    logger.info(f"Test  MAE: {metrics.get('test_mae', 0):.2f}")
    logger.info(f"Test RMSE: {metrics.get('test_rmse', 0):.2f}")

    model_path = str(Config.MODELS_DIR / "price_predictor_model.pkl")
    predictor.save_model(model_path)
    logger.info(f"Model saved to {model_path}")

    logger.info("Training completed successfully")


if __name__ == "__main__":
    main()
