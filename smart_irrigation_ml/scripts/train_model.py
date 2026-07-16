import pandas as pd # type: ignore
import joblib # type: ignore
import os
from sklearn.model_selection import train_test_split # type: ignore
from sklearn.ensemble import RandomForestClassifier # type: ignore
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix # type: ignore

# Load balanced data
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, '..', 'data', 'processed', 'training_data_balanced.csv')

df = pd.read_csv(csv_path)
print(f"✅ Loaded {len(df)} balanced readings")

# Features and target
features = ['soil_moisture', 'temperature', 'humidity']
X = df[features]
y = df['irrigation_needed']

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"🔹 Training set: {len(X_train)} samples")
print(f"🔸 Test set: {len(X_test)} samples")

# Train Random Forest
print("\n🧠 Training Random Forest model...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Test
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n✅ Model Accuracy: {accuracy:.2%}")
print("\n📊 Classification Report:")
print(classification_report(y_test, y_pred))

print("\n📊 Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# Feature importance
importance = pd.DataFrame({
    'Feature': features,
    'Importance': model.feature_importances_
}).sort_values('Importance', ascending=False)

print("\n🔑 Feature Importance:")
print(importance)

# Save model
model_path = os.path.join(script_dir, '..', 'models', 'irrigation_model.pkl')
os.makedirs(os.path.dirname(model_path), exist_ok=True)
joblib.dump(model, model_path)
print(f"\n✅ Model saved to: {model_path}")

# Quick test
print("\n🧪 Testing sample predictions:")
test_samples = [
    [25.0, 28.0, 65.0],  # Low moisture → should irrigate
    [55.0, 30.0, 60.0],  # Good moisture → don't irrigate
    [18.0, 32.0, 70.0],  # Very low → must irrigate
]

for sample in test_samples:
    pred = model.predict([sample])[0]
    prob = model.predict_proba([sample])[0]
    print(f"   Soil: {sample[0]}%, Temp: {sample[1]}°C, Hum: {sample[2]}%")
    print(f"   → Irrigate? {'✅ YES' if pred == 1 else '❌ NO'}")
    print(f"   → Confidence: {max(prob):.2%}")
    print()