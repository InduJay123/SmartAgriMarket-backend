"""
Test script for Yield Predictor
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from predictors.yield_predictor import YieldPredictor


def test_yield_predictor():
    """Test the yield predictor with sample data."""
    print("=== Testing Yield Predictor ===\n")
    
    # Initialize predictor
    predictor = YieldPredictor()
    
    # Check if model is trained
    print(f"Model trained: {predictor.is_trained}")
    
    if not predictor.is_trained:
        print("ERROR: Model not trained!")
        return
    
    # Get model accuracy
    accuracy = predictor.get_accuracy()
    print(f"\nModel Accuracy:")
    print(f"  R² Score: {accuracy['r2']:.4f} ({accuracy['r2']*100:.2f}%)")
    print(f"  MAE: {accuracy['mae']:.2f} kg/ha")
    print(f"  RMSE: {accuracy['rmse']:.2f} kg/ha")
    
    # Test predictions for different crops
    test_cases = [
        {
            'crop_type': 'Tomato',
            'rainfall': 150,
            'temperature': 27,
            'soil_quality': 'good',
            'fertilizer': 50,
            'irrigation': True
        },
        {
            'crop_type': 'Potato',
            'rainfall': 130,
            'temperature': 23,
            'soil_quality': 'excellent',
            'fertilizer': 55,
            'irrigation': True
        },
        {
            'crop_type': 'Carrot',
            'rainfall': 140,
            'temperature': 25,
            'soil_quality': 'good',
            'fertilizer': 52,
            'irrigation': True
        },
    ]
    
    print("\n=== Yield Predictions ===")
    for test in test_cases:
        yield_pred = predictor.predict(test)
        print(f"\n{test['crop_type']}:")
        print(f"  Conditions: {test['rainfall']}mm rain, {test['temperature']}°C, {test['soil_quality']} soil")
        print(f"  Predicted Yield: {yield_pred:,.0f} kg/hectare")


if __name__ == "__main__":
    test_yield_predictor()
