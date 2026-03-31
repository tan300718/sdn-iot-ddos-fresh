import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib

# -------------------------------
# LOAD DATASET
# -------------------------------
try:
    df = pd.read_csv("real_ddos_data.csv")
except FileNotFoundError:
    print("❌ Dataset file not found! Make sure real_ddos_data.csv exists.")
    exit()

# -------------------------------
# BASIC VALIDATION
# -------------------------------
if df.empty:
    print("❌ Dataset is empty!")
    exit()

required_columns = [
    "pkts_per_sec",
    "bytes_per_sec",
    "avg_pkt_size",
    "src_ip_count",
    "label"
]

for col in required_columns:
    if col not in df.columns:
        print(f"❌ Missing column: {col}")
        exit()

print(f"[INFO] Original dataset size: {len(df)}")

# -------------------------------
# CLEAN DATA (VERY IMPORTANT)
# -------------------------------

# Remove invalid/zero rows
df = df[df["pkts_per_sec"] > 0]
df = df[df["bytes_per_sec"] > 0]

print(f"[INFO] After cleaning: {len(df)} rows")

# -------------------------------
# BALANCE DATASET
# -------------------------------
df_normal = df[df["label"] == 0]
df_attack = df[df["label"] == 1]

min_count = min(len(df_normal), len(df_attack))

df_balanced = pd.concat([
    df_normal.sample(min_count, random_state=42),
    df_attack.sample(min_count, random_state=42)
])

print(f"[INFO] Balanced dataset: {len(df_balanced)} rows")

# -------------------------------
# SHUFFLE DATA
# -------------------------------
df_balanced = df_balanced.sample(frac=1, random_state=42).reset_index(drop=True)

# -------------------------------
# FEATURES & LABELS
# -------------------------------
X = df_balanced[[
    "pkts_per_sec",
    "bytes_per_sec",
    "avg_pkt_size",
    "src_ip_count"
]]

y = df_balanced["label"]

# -------------------------------
# TRAIN-TEST SPLIT
# -------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# -------------------------------
# MODEL (IMPROVED)
# -------------------------------
model = RandomForestClassifier(
    n_estimators=300,
    max_depth=12,
    random_state=42
)

print("[INFO] Training model...")
model.fit(X_train, y_train)

# -------------------------------
# EVALUATION
# -------------------------------
y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
print(f"\n✅ Accuracy: {accuracy * 100:.2f}%")

print("\n📊 Classification Report:")
print(classification_report(y_test, y_pred))

# -------------------------------
# SAVE MODEL
# -------------------------------
joblib.dump(model, "ddos_model.pkl")
print("\n💾 Model saved as ddos_model.pkl")
