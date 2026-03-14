"""
Test script for price predictor to verify different vegetables get different prices
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from ml_models.predictors.price_predictor import PricePredictor
from datetime import datetime

print("=== Testing Price Predictor ===\n")

try:
    # Initialize predictor (will auto-train)
    predictor = PricePredictor()
    
    print(f"Model trained: {predictor.is_trained}")
    print(f"Number of products in dataset: {len(predictor.products)}")
    print(f"Products: {predictor.products[:10]}\n")
    
    # Get model accuracy
    accuracy = predictor.get_accuracy()
    print("Model Accuracy:")
    print(f"  R² Score: {accuracy['r2_score']:.4f} ({accuracy['r2_score']*100:.2f}%)")
    print(f"  MAE: Rs. {accuracy['mae']:.2f}")
    print(f"  RMSE: Rs. {accuracy['rmse']:.2f}\n")
    
    # Test predictions for different vegetables
    print("=== Price Predictions ===")
    # Use vegetables that are actually in the dataset
    vegetables = [
        ('Tomato', [150, 148, 152, 155]),      # Recent tomato prices
        ('Carrot', [80, 82, 78, 85]),          # Recent carrot prices  
        ('Cabbage', [60, 58, 62, 65]),         # Recent cabbage prices
        ('Beans', [120, 118, 125, 122]),       # Recent beans prices
        ('Brinjal', [90, 88, 92, 95]),         # Recent brinjal prices
    ]
    
    for veg, hist_prices in vegetables:
        features = {
            'product': veg,
            'date': datetime.now(),
            'historical_prices': hist_prices
        }
        
        try:
            price = predictor.predict(features)
            print(f"{veg}: Rs. {price:.2f} (based on recent prices: {hist_prices[:3]})")
        except Exception as e:
            print(f"{veg}: Error - {str(e)}")
            
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
