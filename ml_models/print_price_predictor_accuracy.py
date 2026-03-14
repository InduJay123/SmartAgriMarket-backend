"""
Script to train the PricePredictor and print accuracy metrics (R², MAE, RMSE) for the market price dataset.
"""

from ml_models.predictors.price_predictor import PricePredictor

if __name__ == "__main__":
    predictor = PricePredictor()
    try:
        metrics = predictor.train()
        print("\n--- Price Predictor Accuracy Metrics ---")
        if 'test_r2' in metrics:
            print(f"Test R²: {metrics['test_r2'] * 100:.2f}%")
        if 'test_mae' in metrics:
            print(f"Test MAE: {metrics['test_mae']:.2f}")
        if 'test_rmse' in metrics:
            print(f"Test RMSE: {metrics['test_rmse']:.2f}")
        if 'train_r2' in metrics:
            print(f"Train R²: {metrics['train_r2'] * 100:.2f}%")
        if 'train_mae' in metrics:
            print(f"Train MAE: {metrics['train_mae']:.2f}")
        if 'train_rmse' in metrics:
            print(f"Train RMSE: {metrics['train_rmse']:.2f}")
    except Exception as e:
        print(f"Error during training or accuracy reporting: {e}")
