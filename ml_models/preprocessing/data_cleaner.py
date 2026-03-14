"""
Data Cleaning Module
Handles missing values, outliers, and data normalization.
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class DataCleaner:
    """Clean and preprocess agricultural data."""

    @staticmethod
    def handle_missing_values(df: pd.DataFrame, strategy: str = 'mean') -> pd.DataFrame:
        """
        Handle missing values in the dataset.

        Args:
            df: Input DataFrame
            strategy: Strategy to handle missing values ('mean', 'median', 'drop')

        Returns:
            DataFrame with missing values handled
        """
        try:
            if strategy == 'mean':
                return df.fillna(df.mean(numeric_only=True))
            elif strategy == 'median':
                return df.fillna(df.median(numeric_only=True))
            elif strategy == 'drop':
                return df.dropna()
            else:
                logger.warning(f"Unknown strategy: {strategy}. Using mean.")
                return df.fillna(df.mean(numeric_only=True))
        except Exception as e:
            logger.error(f"Error handling missing values: {str(e)}")
            raise

    @staticmethod
    def remove_outliers(df: pd.DataFrame, columns: list, method: str = 'iqr') -> pd.DataFrame:
        """
        Remove outliers from the dataset.

        Args:
            df: Input DataFrame
            columns: Columns to check for outliers
            method: Method to detect outliers ('iqr' or 'zscore')

        Returns:
            DataFrame with outliers removed
        """
        try:
            if method == 'iqr':
                for col in columns:
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    df = df[(df[col] >= Q1 - 1.5 * IQR) & (df[col] <= Q3 + 1.5 * IQR)]
            elif method == 'zscore':
                from scipy import stats
                df = df[(np.abs(stats.zscore(df[columns])) < 3).all(axis=1)]
            
            logger.info(f"Outliers removed using {method} method")
            return df
        except Exception as e:
            logger.error(f"Error removing outliers: {str(e)}")
            raise

    @staticmethod
    def normalize_data(df: pd.DataFrame, columns: list) -> pd.DataFrame:
        """
        Normalize numerical columns to 0-1 range.

        Args:
            df: Input DataFrame
            columns: Columns to normalize

        Returns:
            DataFrame with normalized columns
        """
        try:
            df_copy = df.copy()
            for col in columns:
                min_val = df_copy[col].min()
                max_val = df_copy[col].max()
                df_copy[col] = (df_copy[col] - min_val) / (max_val - min_val)
            
            logger.info("Data normalized successfully")
            return df_copy
        except Exception as e:
            logger.error(f"Error normalizing data: {str(e)}")
            raise
