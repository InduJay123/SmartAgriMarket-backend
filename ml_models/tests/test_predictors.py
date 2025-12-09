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
