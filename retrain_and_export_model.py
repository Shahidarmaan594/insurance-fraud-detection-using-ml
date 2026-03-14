"""
Re-train and export model with correct scikit-learn version
Run this LOCALLY on your machine first!
"""

import pickle
import joblib
import pandas as pd
import numpy as np
from sklearn import __version__ as sklearn_version
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
import json
import os

print(f"🔧 Current scikit-learn version: {sklearn_version}")

# ============ STEP 1: Load your training data ============
try:
    data = pd.read_csv('data/fraud_data.csv')  # Adjust path as needed
    print(f"✅ Data loaded: {data.shape}")
except:
    print("❌ No training data found. Using sample data...")
    # Create sample data
    np.random.seed(42)
    data = pd.DataFrame({
        'age': np.random.randint(18, 80, 1000),
        'policy_years': np.random.randint(0, 30, 1000),
        'claim_amount': np.random.randint(100, 100000, 1000),
        'claim_frequency': np.random.randint(0, 10, 1000),
        'fraud': np.random.binomial(1, 0.2, 1000)  # 20% fraud rate
    })

# ============ STEP 2: Prepare data ============
X = data.drop('fraud', axis=1)
y = data['fraud']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ============ STEP 3: Train model ============
print("🔄 Training model...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)

# ============ STEP 4: Evaluate ============
y_pred = model.predict(X_test_scaled)
accuracy = (y_pred == y_test).mean()
print(f"\n✅ Model Accuracy: {accuracy:.2%}")

# ============ STEP 5: Save model (CRITICAL) ============
os.makedirs('models', exist_ok=True)

# Option A: Save with joblib (RECOMMENDED)
print("\n💾 Saving model with joblib...")
joblib.dump(model, 'models/fraud_model.pkl', protocol=4)
print(f"✅ Model saved: models/fraud_model.pkl")

# Option B: Also save with pickle
print("💾 Saving model with pickle...")
with open('models/fraud_model_backup.pkl', 'wb') as f:
    pickle.dump(model, f, protocol=4)

# Option C: Save scaler (needed for predictions)
print("💾 Saving scaler...")
joblib.dump(scaler, 'models/scaler.pkl', protocol=4)

# ============ STEP 6: Save metrics ============
metrics = {
    'accuracy': float(accuracy),
    'sklearn_version': sklearn_version,
    'model_type': 'RandomForestClassifier',
    'n_features': X_train_scaled.shape[1],
    'training_samples': len(X_train)
}

with open('models/model_metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)

print("\n" + "="*50)
print("✅ Model export complete!")
print("="*50)
print(f"\n📁 Files created:")
print(f"  ✓ models/fraud_model.pkl (joblib format)")
print(f"  ✓ models/fraud_model_backup.pkl (pickle format)")
print(f"  ✓ models/scaler.pkl")
print(f"  ✓ models/model_metrics.json")
print(f"\n🔧 scikit-learn version: {sklearn_version}")
print(f"\n⬆️  Now push these files to GitHub!")
