import traceback
import joblib
try:
    joblib.load('ml_models/models/random_forest_flood_model.pkl')
    print('success')
except Exception as e:
    traceback.print_exc()
