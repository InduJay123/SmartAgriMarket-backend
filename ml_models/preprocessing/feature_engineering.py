"""
Feature Engineering Module
Creates and transforms features for ML models.
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Engineer features for agricultural predictions."""

    @staticmethod
    def create_temporal_features(df: pd.DataFrame, date_column: str) -> pd.DataFrame:
        """
        Create temporal features from date column.

        Args:
            df: Input DataFrame
            date_column: Name of date column

        Returns:
            DataFrame with temporal features
        """
        try:
            df[date_column] = pd.to_datetime(df[date_column])
            df['year'] = df[date_column].dt.year
            df['month'] = df[date_column].dt.month
            df['quarter'] = df[date_column].dt.quarter
            df['day_of_year'] = df[date_column].dt.dayofyear
            
            logger.info("Temporal features created")
            return df
        except Exception as e:
            logger.error(f"Error creating temporal features: {str(e)}")
            raise

    @staticmethod
    def create_lag_features(df: pd.DataFrame, column: str, lags: list) -> pd.DataFrame:
        """
        Create lagged features for time series data.

        Args:
            df: Input DataFrame
            column: Column to create lags for
            lags: List of lag values

        Returns:
            DataFrame with lag features
        """
        try:
            for lag in lags:
                df[f'{column}_lag_{lag}'] = df[column].shift(lag)
            
            logger.info(f"Lag features created for {column}")
            return df
        except Exception as e:
            logger.error(f"Error creating lag features: {str(e)}")
            raise

    @staticmethod
    def create_rolling_features(df: pd.DataFrame, column: str, windows: list) -> pd.DataFrame:
        """
        Create rolling window features.

        Args:
            df: Input DataFrame
            column: Column to create rolling features for
            windows: List of window sizes

        Returns:
            DataFrame with rolling features
        """
        try:
            for window in windows:
                df[f'{column}_rolling_mean_{window}'] = df[column].rolling(window=window).mean()
                df[f'{column}_rolling_std_{window}'] = df[column].rolling(window=window).std()
            
            logger.info(f"Rolling features created for {column}")
            return df
        except Exception as e:
            logger.error(f"Error creating rolling features: {str(e)}")
            raise

    @staticmethod
    def encode_categorical(df: pd.DataFrame, columns: list) -> pd.DataFrame:
        """
        Encode categorical variables.

        Args:
            df: Input DataFrame
            columns: Categorical columns to encode

        Returns:
            DataFrame with encoded categorical features
        """
        try:
            from sklearn.preprocessing import LabelEncoder
            
            df_copy = df.copy()
            le_dict = {}
            
            for col in columns:
                le = LabelEncoder()
                df_copy[col] = le.fit_transform(df_copy[col].astype(str))
                le_dict[col] = le
            
            logger.info(f"Categorical features encoded: {columns}")
            return df_copy
        except Exception as e:
            logger.error(f"Error encoding categorical features: {str(e)}")
            raise
