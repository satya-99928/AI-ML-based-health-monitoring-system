import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

import joblib

# -----------------------------
# 1. LOAD EXCEL DATA
# -----------------------------
df = pd.read_excel(r"C:\Users\Shashwat\Downloads\new_dataset.xlsx")

# -----------------------------
# 2. DROP TIMESTAMP (NOT A FEATURE)
# -----------------------------
df = df.drop(columns=["timestamp"])

# -----------------------------
# 3. CREATE LABEL (RULE-BASED)
# 0 = Normal, 1 = Abnormal
# -----------------------------
def create_label(row):
    if (
        row["bpm"] < 60 or row["bpm"] > 100 or
        row["spo2"] < 95 or
        row["temperature_c"] < 36.1 or row["temperature_c"] > 37.2
    ):
        return 1
    return 0

df["label"] = df.apply(create_label, axis=1)

# -----------------------------
# 4. FEATURES & TARGET
# -----------------------------
X = df.drop(columns=["label"])
y = df["label"]

# -----------------------------
# 5. SCALING
# -----------------------------
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# -----------------------------
# 6. TRAIN-TEST SPLIT
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# -----------------------------
# 7. RANDOM FOREST MODEL
# -----------------------------
rf_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    random_state=42,
    n_jobs=-1
)

# -----------------------------
# 8. TRAIN
# -----------------------------
rf_model.fit(X_train, y_train)

# -----------------------------
# 9. EVALUATION
# -----------------------------
y_pred = rf_model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# -----------------------------
# 10. SAVE OUTPUT FILES
# -----------------------------
joblib.dump(rf_model, "health_rf_model.pkl")
joblib.dump(scaler, "health_scaler.pkl")

print("\nSaved: health_rf_model.pkl & health_scaler.pkl")
