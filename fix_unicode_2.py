with open('ml_models/predictors/flood_predictor.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'Model loaded successfully from' in line:
        lines[i] = '            print(f"Model loaded successfully from {model_path}")\n'
    elif 'Error loading model:' in line:
        lines[i] = '            print(f"Error loading model: {str(e)}")\n'

with open('ml_models/predictors/flood_predictor.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
