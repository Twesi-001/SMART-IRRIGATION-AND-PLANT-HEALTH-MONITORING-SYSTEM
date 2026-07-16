import pandas as pd # type: ignore
import os

# Get the current script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, '..', 'data', 'raw', 'training_data.csv')

# Load the CSV file with tab separator
df = pd.read_csv(csv_path, sep='\t')
print(f"✅ Loaded {len(df)} readings")

# Show column names
print(f"\n📋 Original columns: {list(df.columns)}")

# Clean column names by splitting if they contain tabs
if len(df.columns) == 1 and '\t' in df.columns[0]:
    # If all columns are in one string, split by tab
    col_names = df.columns[0].split('\t')
    # Split the data similarly
    df = df[df.columns[0]].str.split('\t', expand=True)
    df.columns = col_names
    print(f"📋 Cleaned columns: {list(df.columns)}")

# Convert columns to numeric
df['soil_moisture'] = pd.to_numeric(df['soil_moisture'])
df['temperature'] = pd.to_numeric(df['temperature'])
df['humidity'] = pd.to_numeric(df['humidity'])

# Add labels based on threshold
threshold = 30.0  # Your moisture threshold
df['irrigation_needed'] = (df['soil_moisture'] < threshold).astype(int)

# Check balance
print("\n📊 Data Balance:")
print("-" * 30)
class_0 = len(df[df['irrigation_needed'] == 0])
class_1 = len(df[df['irrigation_needed'] == 1])
total = len(df)

print(f"Class 0 (No irrigation needed): {class_0} readings ({class_0/total*100:.1f}%)")
print(f"Class 1 (Irrigation needed):  {class_1} readings ({class_1/total*100:.1f}%)")
print("-" * 30)

if 40 < (class_1/total*100) < 60:
    print("✅ Data is well balanced! Ready for training.")
else:
    print("⚠️ Data is imbalanced. We'll need to balance it before training.")

# Show sample data
print("\n📋 Sample Data (first 5 rows):")
print(df.head())