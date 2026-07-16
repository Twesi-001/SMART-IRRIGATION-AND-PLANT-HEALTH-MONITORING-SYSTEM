import pandas as pd # type: ignore
import joblib # type: ignore
import os
from sklearn.model_selection import train_test_split # type: ignore
from sklearn.ensemble import RandomForestClassifier # type: ignore
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix # type: ignore

# Load balanced data
csv_path = '../data/processed/training_data_balanced_all_crops.csv'
df = pd.read_csv(csv_path)
print(f"✅ Loaded {len(df)} balanced readings")

# Show columns
print(f"📋 Columns: {list(df.columns)}")

# Define crop thresholds
crop_thresholds = {
    1: 35,   # Maize
    2: 45,   # Tomato
    3: 40,   # Onion
    4: 55,   # Cabbage
    5: 35,   # Mango
    6: 60,   # Banana
    7: 40,   # Pineapple
    8: 45,   # Passion Fruit
    9: 50,   # Carrot
    10: 45,  # Capsicum
    11: 50,  # Eggplant
    12: 55,  # Sukuma Wiki
    13: 55,  # Spinach
    14: 40,  # Beans
    15: 40,  # Garlic
    16: 50,  # Strawberry
    17: 55,  # Lettuce
    18: 50,  # Cucumber
    19: 40,  # Watermelon
    20: 45   # Pumpkin
}

# Add irrigation needed based on crop-specific threshold
def get_irrigation_needed(row):
    threshold = crop_thresholds.get(row['node_id'], 40)  # Default 40 if not found
    return 1 if row['soil_moisture'] < threshold else 0

df['irrigation_needed'] = df.apply(get_irrigation_needed, axis=1)

# Check balance
print(f"\n📊 Irrigation Needed Distribution:")
print(df['irrigation_needed'].value_counts())

# Features and target
features = ['soil_moisture', 'temperature', 'humidity', 'node_id']
X = df[features]
y = df['irrigation_needed']

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"🔹 Training set: {len(X_train)} samples")
print(f"🔸 Test set: {len(X_test)} samples")

# Train Random Forest
print("\n🧠 Training Random Forest with crop type...")
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
model_path = '../models/irrigation_model_all_crops.pkl'
os.makedirs(os.path.dirname(model_path), exist_ok=True)
joblib.dump(model, model_path)
print(f"\n✅ Model saved to: {model_path}")

# Test with different crops
print("\n🧪 Testing predictions for different crops:")

test_data = [
    {"node_id": 1, "crop": "Maize", "threshold": 35, "moisture": 25},
    {"node_id": 1, "crop": "Maize", "threshold": 35, "moisture": 50},
    {"node_id": 2, "crop": "Tomato", "threshold": 45, "moisture": 35},
    {"node_id": 2, "crop": "Tomato", "threshold": 45, "moisture": 60},
    {"node_id": 4, "crop": "Cabbage", "threshold": 55, "moisture": 45},
    {"node_id": 4, "crop": "Cabbage", "threshold": 55, "moisture": 70},
    {"node_id": 6, "crop": "Banana", "threshold": 60, "moisture": 45},
    {"node_id": 6, "crop": "Banana", "threshold": 60, "moisture": 75},
]

for test in test_data:
    sample = [[test["moisture"], 28.0, 60.0, test["node_id"]]]
    pred = model.predict(sample)[0]
    prob = model.predict_proba(sample)[0]
    status = "✅ IRRIGATE" if pred == 1 else "❌ NO IRRIGATION"
    print(f"   {test['crop']} (Threshold: {test['threshold']}%) - Moisture: {test['moisture']}% → {status} (Confidence: {max(prob):.2%})")