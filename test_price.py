"""
End-to-end test for price prediction pipeline.
Verifies: load saved .pkl -> predict for various products/dates -> confirm non-mock outputs.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ml_models.predictors.price_predictor import PricePredictor

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'ml_models', 'models', 'price_predictor.pkl')

def main():
    print("=" * 60)
    print("  End-to-End Price Prediction Test")
    print("=" * 60)

    # 1. Load from .pkl
    assert os.path.exists(MODEL_PATH), f"Model not found: {MODEL_PATH}"
    predictor = PricePredictor(model_path=MODEL_PATH, auto_train=False)
    assert predictor.is_trained, "Model did not load as trained"
    print(f"[OK] Model loaded from {MODEL_PATH}")
    print(f"     Products: {predictor.products}")
    print(f"     Features: {len(predictor.feature_columns)}")

    # 2. Predictions for different products/dates
    test_cases = [
        {"product": "Tomato", "date": "2025-06-15"},
        {"product": "Beans", "date": "2025-06-15"},
        {"product": "Cabbage", "date": "2025-06-15"},
        {"product": "Tomato", "date": "2025-01-10"},
        {"product": "Tomato", "date": "2025-12-01"},
        {"product": "Carrot", "date": "2025-03-20"},
        {"product": "Brinjal", "date": "2025-09-01"},
    ]

    print(f"\n{'Product':<15} {'Date':<15} {'Predicted (LKR)':>15}")
    print("-" * 47)

    results = []
    for tc in test_cases:
        price = predictor.predict(tc)
        results.append(price)
        print(f"{tc['product']:<15} {tc['date']:<15} {price:>15.2f}")

    # 3. Verify predictions are NOT all the same (not mocked)
    unique_prices = len(set(round(p, 2) for p in results))
    assert unique_prices > 1, f"All predictions are identical ({results[0]}) — likely mocked!"
    print(f"\n[OK] {unique_prices} unique price values across {len(results)} predictions — not mocked")

    # 4. Verify all prices are positive
    assert all(p > 0 for p in results), "Some predictions are zero or negative"
    print("[OK] All predictions are positive")

    # 5. Check model accuracy metrics
    acc = predictor.get_accuracy()
    print(f"\n  Model R²:   {acc['r2_score']:.4f}")
    print(f"  Model MAE:  {acc['mae']:.2f}")
    print(f"  Model RMSE: {acc['rmse']:.2f}")

    # 6. Test future prediction series
    future = predictor.predict_future("Tomato", days_ahead=7)
    assert len(future) == 7, f"Expected 7 forecasts, got {len(future)}"
    print(f"\n  7-day forecast for Tomato:")
    for f in future:
        print(f"    {f['date']}: {f['predicted_price']:.2f} LKR")

    print("\n" + "=" * 60)
    print("  ALL TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
