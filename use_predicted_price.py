import os
import sys
from datetime import datetime

# Add root directory to python path if run from command line
sys.path.insert(0, os.path.dirname(__file__))

# Import the predictors
from ml_models.predictors.price_predictor import PricePredictor
from ml_models.predictors.demand_predictor import DemandPredictor

def main():
    print("=== Predicting Price and Using it as Input ===")

    # 1. Initialize the PricePredictor (it automatically loads/trains the model)
    model_path = os.path.join(os.path.dirname(__file__), 'ml_models', 'models', 'price_predictor_model.pkl')
    
    print("1. Loading Price Predictor...")
    price_predictor = PricePredictor(model_path=model_path if os.path.exists(model_path) else None)
    
    # 2. Define the inputs for the price prediction
    target_crop = "Carrot"
    prediction_date = datetime.now()
    historical_prices = [80, 82, 78, 85] # Optional: Provide recent prices
    
    price_inputs = {
        'product': target_crop,
        'date': prediction_date,
        'historical_prices': historical_prices
    }

    print(f"   Inputs for Price Predictor: {price_inputs}")

    # 3. Get the prediction
    try:
        predicted_price = price_predictor.predict(price_inputs)
        print(f"\n✅ Predicted Price for {target_crop}:\n   Rs. {predicted_price:.2f} per kg")
    except Exception as e:
        print(f"Error predicting price: {str(e)}")
        return

    print("\n----------------------------------------------------\n")

    # 4. Use the predicted price as an input elsewhere
    
    print("2. Feeding Predicted Price into another process...")
    print(f"   (e.g., Using Price = {predicted_price:.2f} to calculate revenue or evaluate demand elasticity)")
    
    # Example 4a: Simple revenue calculation using predicted price
    expected_sales_kg = 500
    expected_revenue = expected_sales_kg * predicted_price
    print(f"   [Process A] Revenue Estimation: If we sell {expected_sales_kg}kg, Expected Revenue = Rs. {expected_revenue:.2f}")

    # Example 4b: Update historical prices with the newly predicted price (Recursive Forecasting)
    print("\n   [Process B] Using predicted price as an input for the NEXT day's prediction")
    
    next_day = prediction_date.replace(day=prediction_date.day + 1)
    # Shift historical prices and append the predicted price
    new_historical_prices = historical_prices[1:] + [predicted_price]
    
    next_day_inputs = {
        'product': target_crop,
        'date': next_day,
        'historical_prices': new_historical_prices
    }
    
    try:
        next_day_price = price_predictor.predict(next_day_inputs)
        print(f"   Inputs for Next Day: {next_day_inputs}")
        print(f"   ✅ Predicted Price for Next Day ({target_crop}): Rs. {next_day_price:.2f} per kg")
    except Exception as e:
        print(f"   Error predicting next day price: {str(e)}")

if __name__ == "__main__":
    main()
