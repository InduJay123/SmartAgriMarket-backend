"""
Unit tests for predictors.
"""

import unittest
import numpy as np
from ml_models.predictors import YieldPredictor, PricePredictor, DemandPredictor


class TestYieldPredictor(unittest.TestCase):
    """Test cases for YieldPredictor."""

    def setUp(self):
        """Set up test fixtures."""
        self.predictor = YieldPredictor()

    def test_initialization(self):
        """Test predictor initialization."""
        self.assertFalse(self.predictor.is_trained)
        self.assertIsNone(self.predictor.model)

    def test_get_model_info(self):
        """Test getting model information."""
        info = self.predictor.get_model_info()
        self.assertEqual(info['model_name'], 'Yield Predictor')
        self.assertFalse(info['is_trained'])


class TestPricePredictor(unittest.TestCase):
    """Test cases for PricePredictor."""

    def setUp(self):
        """Set up test fixtures."""
        self.predictor = PricePredictor()

    def test_initialization(self):
        """Test predictor initialization."""
        self.assertFalse(self.predictor.is_trained)
        self.assertIsNone(self.predictor.model)

    def test_get_model_info(self):
        """Test getting model information."""
        info = self.predictor.get_model_info()
        self.assertEqual(info['model_name'], 'Price Predictor')
        self.assertFalse(info['is_trained'])

        def test_train_and_report_accuracy(self):
            """Train the price predictor and print accuracy metrics."""
            try:
                metrics = self.predictor.train()
                print("\n--- Price Predictor Accuracy Metrics ---")
                if 'test_r2' in metrics:
                    print(f"Test R²: {metrics['test_r2'] * 100:.2f}%")
                if 'test_mae' in metrics:
                    print(f"Test MAE: {metrics['test_mae']:.2f}")
                if 'test_rmse' in metrics:
                    print(f"Test RMSE: {metrics['test_rmse']:.2f}")
                # Also print training metrics for reference
                if 'train_r2' in metrics:
                    print(f"Train R²: {metrics['train_r2'] * 100:.2f}%")
                if 'train_mae' in metrics:
                    print(f"Train MAE: {metrics['train_mae']:.2f}")
                if 'train_rmse' in metrics:
                    print(f"Train RMSE: {metrics['train_rmse']:.2f}")
            except Exception as e:
                print(f"Error during training or accuracy reporting: {e}")


class TestDemandPredictor(unittest.TestCase):
    """Test cases for DemandPredictor."""

    def setUp(self):
        """Set up test fixtures."""
        self.predictor = DemandPredictor()

    def test_initialization(self):
        """Test predictor initialization."""
        self.assertFalse(self.predictor.is_trained)
        self.assertIsNone(self.predictor.model)

    def test_get_model_info(self):
        """Test getting model information."""
        info = self.predictor.get_model_info()
        self.assertEqual(info['model_name'], 'Demand Predictor')
        self.assertFalse(info['is_trained'])


if __name__ == '__main__':
    unittest.main()
