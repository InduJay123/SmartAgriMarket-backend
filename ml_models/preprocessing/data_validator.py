"""
Data Validation Module
Validates data quality and consistency.
"""

import pandas as pd
import logging

logger = logging.getLogger(__name__)


class DataValidator:
    """Validate agricultural data quality."""

    @staticmethod
    def check_data_quality(df: pd.DataFrame) -> dict:
        """
        Check overall data quality.

        Args:
            df: Input DataFrame

        Returns:
            Dictionary with quality metrics
        """
        try:
            quality_report = {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'missing_values': df.isnull().sum().to_dict(),
                'missing_percentage': (df.isnull().sum() / len(df) * 100).to_dict(),
                'duplicate_rows': df.duplicated().sum(),
                'data_types': df.dtypes.to_dict(),
            }
            
            logger.info("Data quality check completed")
            return quality_report
        except Exception as e:
            logger.error(f"Error checking data quality: {str(e)}")
            raise

    @staticmethod
    def validate_schema(df: pd.DataFrame, required_columns: list) -> bool:
        """
        Validate that required columns exist.

        Args:
            df: Input DataFrame
            required_columns: List of required column names

        Returns:
            True if valid, False otherwise
        """
        try:
            missing_cols = [col for col in required_columns if col not in df.columns]
            
            if missing_cols:
                logger.warning(f"Missing columns: {missing_cols}")
                return False
            
            logger.info("Schema validation passed")
            return True
        except Exception as e:
            logger.error(f"Error validating schema: {str(e)}")
            raise

    @staticmethod
    def validate_value_ranges(df: pd.DataFrame, column: str, min_val: float = None, max_val: float = None) -> bool:
        """
        Validate that column values are within expected range.

        Args:
            df: Input DataFrame
            column: Column to validate
            min_val: Minimum acceptable value
            max_val: Maximum acceptable value

        Returns:
            True if valid, False otherwise
        """
        try:
            if min_val is not None:
                if (df[column] < min_val).any():
                    logger.warning(f"Values below minimum {min_val} found in {column}")
                    return False
            
            if max_val is not None:
                if (df[column] > max_val).any():
                    logger.warning(f"Values above maximum {max_val} found in {column}")
                    return False
            
            logger.info(f"Value range validation passed for {column}")
            return True
        except Exception as e:
            logger.error(f"Error validating value ranges: {str(e)}")
            raise
