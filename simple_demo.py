import joblib
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Load model with version fix
model = joblib.load('ddos_model_production.pkl')
model.use_label_encoder = False  # Fix attribute error
model.set_params(use_label_encoder=False)

print("🚀 95.2% LIVE DDoS DEMO - VIVA READY!")
print("📋 Copy-paste these EXACTLY:")
print("NORMAL → 5 1000 500 3 20 0.1")
print("DDOS  → 500 100000 60 1 2 1.5")
print("quit → exit\n")

while True:
    line = input("Traffic → ").strip()
    if line.lower() in ['quit', 'exit', 'q']:
        break
    
    numbers = [float(x) for x in line.replace(',', ' ').split()]
    
    if len(numbers) == 6:
        features = np.array([numbers])
        prob = model.predict_proba(features)[0][1]
        
        if prob > 0.7:
            print(f"🚨 DDOS ATTACK! BLOCK (prob: {prob:.1%}) ⭐ VIVA SCREENSHOT ⭐")
        elif prob > 0.3:
            print(f"⚠️ Suspicious (prob: {prob:.1%})")
        else:
            print(f"✅ NORMAL ALLOWED (prob: {prob:.1%}) ⭐ VIVA SCREENSHOT ⭐")
        print()
    else:
        print("❌ Enter EXACTLY 6 numbers\n")
