"""
End-to-end verification of all ML predictors.
Run: python verify_predictors.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

def test_price_predictor():
    print("=== PricePredictor ===")
    from ml_models.predictors import PricePredictor
    pp = PricePredictor()
    print(f"  Trained: {pp.is_trained}")
    assert pp.is_trained, "PricePredictor did not auto-train!"
    
    price = pp.predict({'product': 'Tomato', 'date': '2025-06-15'})
    print(f"  Tomato price prediction: Rs. {price:.2f}")
    assert price > 0, f"Price should be > 0, got {price}"
    
    accuracy = pp.get_accuracy()
    print(f"  R2: {accuracy.get('r2_score', 0):.4f}")
    print(f"  MAE: {accuracy.get('mae', 0):.2f}")
    print(f"  RMSE: {accuracy.get('rmse', 0):.2f}")
    print("  PASSED\n")
    return accuracy


def test_yield_predictor():
    print("=== YieldPredictor ===")
    from ml_models.predictors import YieldPredictor
    yp = YieldPredictor()
    print(f"  Trained: {yp.is_trained}")
    assert yp.is_trained, "YieldPredictor model not loaded!"
    
    y = yp.predict({'crop_type': 'Carrot'})
    print(f"  Carrot yield prediction: {y:.2f} kg/ha")
    assert y > 0, f"Yield should be > 0, got {y}"
    
    series = yp.forecast(crop_type='Carrot', months=3)
    print(f"  3-month forecast: {[s['predicted_yield'] for s in series]}")
    assert len(series) == 3, f"Expected 3 forecast points, got {len(series)}"
    print("  PASSED\n")


def test_demand_predictor():
    print("=== DemandPredictor ===")
    import pandas as pd
    from ml_models.predictors import DemandPredictor
    
    dp = DemandPredictor()
    dp.load()
    
    excel_path = os.path.join('data', 'demand_dataset.xlsx')
    assert os.path.exists(excel_path), f"Demand dataset not found: {excel_path}"
    
    df = pd.read_excel(excel_path)
    result = dp.forecast_days('Cabbage', 7, 'Stable', df)
    
    total = result['predicted_total_tonnes']
    days = len(result['data'])
    print(f"  Cabbage 7-day demand total: {total:.2f} tonnes")
    print(f"  Days forecast: {days}")
    print(f"  Model trained at: {result.get('model', {}).get('trained_at', 'N/A')}")
    print(f"  Train MAE: {result.get('model', {}).get('train_mae', 'N/A')}")
    assert days == 7, f"Expected 7 days, got {days}"
    assert total > 0, f"Total demand should be > 0, got {total}"
    print("  PASSED\n")


if __name__ == '__main__':
    print("=" * 60)
    print("ML PREDICTOR VERIFICATION")
    print("=" * 60 + "\n")
    
    try:
        price_accuracy = test_price_predictor()
    except Exception as e:
        print(f"  FAILED: {e}\n")
        price_accuracy = None
    
    try:
        test_yield_predictor()
    except Exception as e:
        print(f"  FAILED: {e}\n")
    
    try:
        test_demand_predictor()
    except Exception as e:
        print(f"  FAILED: {e}\n")
    
    print("=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)
