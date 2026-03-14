"""
Unit tests for data preprocessing.
"""

import unittest
import pandas as pd
import numpy as np
from ml_models.preprocessing import DataCleaner, DataValidator, FeatureEngineer


class TestDataCleaner(unittest.TestCase):
    """Test cases for DataCleaner."""

    def setUp(self):
        """Set up test fixtures."""
        self.df = pd.DataFrame({
            'A': [1, 2, np.nan, 4, 5],
            'B': [10, 20, 30, 40, 50],
        })

    def test_handle_missing_values_mean(self):
        """Test handling missing values with mean strategy."""
        result = DataCleaner.handle_missing_values(self.df, strategy='mean')
        self.assertFalse(result.isnull().any().any())

    def test_handle_missing_values_drop(self):
        """Test handling missing values with drop strategy."""
        result = DataCleaner.handle_missing_values(self.df, strategy='drop')
        self.assertEqual(len(result), 4)


class TestDataValidator(unittest.TestCase):
    """Test cases for DataValidator."""

    def setUp(self):
        """Set up test fixtures."""
        self.df = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': [10, 20, 30, 40, 50],
        })

    def test_validate_schema_valid(self):
        """Test schema validation with valid columns."""
        result = DataValidator.validate_schema(self.df, ['A', 'B'])
        self.assertTrue(result)

    def test_validate_schema_invalid(self):
        """Test schema validation with missing columns."""
        result = DataValidator.validate_schema(self.df, ['A', 'C'])
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
