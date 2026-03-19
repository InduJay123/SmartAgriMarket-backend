"""
Training script for crop price prediction model.
Trains a RandomForest model on vegetable_prices.csv and saves the .pkl file.

Usage:
    python -m ml_models.training.train_price_model
"""

import os
import sys
import logging

# Add project root to path so imports work when run as a module
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from ml_models.predictors.price_predictor import PricePredictor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Paths
DATA_PATH = os.path.join(project_root, 'data', 'vegetable_prices.csv')
MODEL_SAVE_PATH = os.path.join(project_root, 'ml_models', 'models', 'price_predictor.pkl')


def main():
    """Train the price prediction model and save to disk."""
    print("=" * 60)
    print("  Price Prediction Model — Training Pipeline")
    print("=" * 60)

    # --- 1. Validate dataset exists ---
    if not os.path.exists(DATA_PATH):
        print(f"\n[ERROR] Dataset not found: {DATA_PATH}")
        sys.exit(1)

    print(f"\n[INFO] Dataset: {DATA_PATH}")
    print(f"[INFO] Model will be saved to: {MODEL_SAVE_PATH}")

    # --- 2. Create predictor (without auto-train) and train ---
    predictor = PricePredictor(auto_train=False)

    print("\n[STEP 1] Loading data and training model...")
    metrics = predictor.train(
        filepath=DATA_PATH,
        target_column='Pettah_Wholesale',
        n_estimators=200,
        max_depth=None,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        add_noise=False,
    )

    # --- 3. Print metrics ---
    print("\n" + "=" * 60)
    print("  Training Results")
    print("=" * 60)

    if 'train_r2' in metrics:
        print(f"  Train R²:   {metrics['train_r2'] * 100:.2f}%")
    if 'train_mae' in metrics:
        print(f"  Train MAE:  {metrics['train_mae']:.2f}")
    if 'train_rmse' in metrics:
        print(f"  Train RMSE: {metrics['train_rmse']:.2f}")

    print()
    if 'test_r2' in metrics:
        print(f"  Test  R²:   {metrics['test_r2'] * 100:.2f}%")
    if 'test_mae' in metrics:
        print(f"  Test  MAE:  {metrics['test_mae']:.2f}")
    if 'test_rmse' in metrics:
        print(f"  Test  RMSE: {metrics['test_rmse']:.2f}")

    # --- 4. Save model ---
    print(f"\n[STEP 2] Saving model to {MODEL_SAVE_PATH}...")
    os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)
    predictor.save_model(MODEL_SAVE_PATH)
    print(f"[OK] Model saved ({os.path.getsize(MODEL_SAVE_PATH):,} bytes)")

    # --- 5. Verify saved model loads correctly ---
    print("\n[STEP 3] Verifying saved model loads correctly...")
    test_predictor = PricePredictor(model_path=MODEL_SAVE_PATH, auto_train=False)
    if test_predictor.is_trained:
        sample = test_predictor.predict({'product': 'Tomato', 'date': '2025-06-15'})
        print(f"[OK] Model loaded and verified. Sample prediction (Tomato, 2025-06-15): {sample:.2f} LKR")
    else:
        print("[WARNING] Model loaded but is_trained is False")

    # --- 6. Print top features ---
    print("\n[STEP 4] Top 10 Feature Importances:")
    importance = predictor.get_feature_importance(top_n=10)
    for i, (feat, imp) in enumerate(importance.items(), 1):
        print(f"  {i:2}. {feat:30s} {imp:.4f}")

    print("\n" + "=" * 60)
    print("  Training complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
