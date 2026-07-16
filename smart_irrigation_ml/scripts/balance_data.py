import pandas as pd # type: ignore
import os

# Load the data
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, '..', 'data', 'raw', 'training_data.csv')

# Load with tab separator
df = pd.read_csv(csv_path, sep='\t')

# Clean columns
df.columns = ['soil_moisture', 'temperature', 'humidity']

# Convert to numeric
df['soil_moisture'] = pd.to_numeric(df['soil_moisture'])
df['temperature'] = pd.to_numeric(df['temperature'])
df['humidity'] = pd.to_numeric(df['humidity'])

# Add labels
threshold = 30.0
df['irrigation_needed'] = (df['soil_moisture'] < threshold).astype(int)

# Separate classes
class_0 = df[df['irrigation_needed'] == 0]  # No irrigation needed
class_1 = df[df['irrigation_needed'] == 1]  # Irrigation needed

print(f"Class 0: {len(class_0)} readings")
print(f"Class 1: {len(class_1)} readings")

# Oversample class 1 to match class 0
if len(class_1) < len(class_0):
    # Randomly sample from class_1 with replacement
    class_1_oversampled = class_1.sample(n=len(class_0), replace=True, random_state=42)
    balanced_df = pd.concat([class_0, class_1_oversampled], ignore_index=True)
    print(f"\n✅ Balanced: {len(balanced_df)} readings")
else:
    balanced_df = df
    print("\n✅ Data already balanced")

# Shuffle
balanced_df = balanced_df.sample(frac=1, random_state=42).reset_index(drop=True)

# Save balanced data
output_path = os.path.join(script_dir, '..', 'data', 'processed', 'training_data_balanced.csv')
balanced_df.to_csv(output_path, index=False)
print(f"\n✅ Balanced data saved to: {output_path}")

# Check final balance
print("\n📊 Final Balance:")
print(f"Class 0: {len(balanced_df[balanced_df['irrigation_needed'] == 0])} readings")
print(f"Class 1: {len(balanced_df[balanced_df['irrigation_needed'] == 1])} readings")