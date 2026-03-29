import pandas as pd
import numpy as np
import joblib
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split

np.random.seed(42)

print("🔄 Generating 100,000 samples (realistic difficulty)...")

normal_features = []
ddos_features = []

# NORMAL TRAFFIC (80,000)
for _ in range(80000):
    normal_features.append({
        'pkts_per_sec': np.random.normal(150, 100),   # heavy overlap
        'bytes_per_sec': np.random.normal(80000, 60000),
        'avg_pkt_size': np.random.uniform(40, 1500),
        'src_ip_count': np.random.uniform(1, 100),
        'duration': np.random.uniform(1, 300),
        'pps_ratio': np.random.normal(0.7, 0.5),
        'label': 0
    })

# DDOS TRAFFIC (20,000)
for _ in range(20000):
    ddos_features.append({
        'pkts_per_sec': np.random.normal(300, 200),   # overlaps strongly
        'bytes_per_sec': np.random.normal(150000, 100000),
        'avg_pkt_size': np.random.uniform(40, 600),
        'src_ip_count': np.random.uniform(1, 300),
        'duration': np.random.uniform(0.1, 200),
        'pps_ratio': np.random.normal(1.2, 0.7),
        'label': 1
    })

df = pd.DataFrame(normal_features + ddos_features)

# -----------------------------
# CLEANUP (remove negatives from normal distributions)
# -----------------------------
for col in df.columns[:-1]:
    df[col] = df[col].clip(lower=0.01)

# -----------------------------
# ADD FEATURE NOISE
# -----------------------------
noise = np.random.normal(0, 0.1, df.shape)
df.iloc[:, :-1] += noise[:, :-1]

# -----------------------------
# ADD LABEL NOISE (VERY IMPORTANT)
# -----------------------------
flip_idx = np.random.choice(df.index, size=int(0.05 * len(df)), replace=False)
df.loc[flip_idx, 'label'] = 1 - df.loc[flip_idx, 'label']

print(f"📊 Dataset: {len(df):,} samples")
print(f"DDoS ratio: {df['label'].mean():.2%}")

# -----------------------------
# SPLIT
# -----------------------------
X = df.drop('label', axis=1).astype(float)
y = df['label'].astype(int)

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.3,
    random_state=42,
    stratify=y
)

print(f"\n📊 Train size: {len(X_train):,}")
print(f"📊 Test size: {len(X_test):,}")

# -----------------------------
# MODEL
# -----------------------------
print("\n✅ Training XGBoost...")

model = XGBClassifier(
    n_estimators=400,
    max_depth=6,
    learning_rate=0.07,
    subsample=0.9,
    colsample_bytree=0.9,
    scale_pos_weight=2.0,
    random_state=42,
    eval_metric='logloss'
)

model.fit(X_train, y_train)

# -----------------------------
# EVALUATION
# -----------------------------
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n🎯 Test Accuracy: {accuracy:.2%}")

print("\n📊 Classification Report:")
print(classification_report(y_test, y_pred, target_names=['Normal', 'DDoS']))

# -----------------------------
# SAVE
# -----------------------------
joblib.dump(model, 'ddos_model_new.pkl')
print("\n💾 Model saved as ddos_model_new.pkl")

# -----------------------------
# TEST CASES
# -----------------------------
print("\n🧪 Manual Testing:")

normal_sample = [[120, 90000, 900, 40, 150, 0.6]]
ddos_sample = [[400, 250000, 100, 10, 20, 1.8]]

print("Normal Traffic DDoS Probability:",
      model.predict_proba(normal_sample)[0][1])

print("DDoS Traffic Probability:",
      model.predict_proba(ddos_sample)[0][1])
