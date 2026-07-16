import pandas as pd # type: ignore
import os

# Load the data with tab separator
csv_path = '../data/raw/training_data_all_crops.csv'
df = pd.read_csv(csv_path, sep='\t')
print(f"✅ Loaded {len(df)} readings")

# Clean column names (remove extra spaces)
df.columns = df.columns.str.strip()

# Show column names
print(f"\n📋 Columns: {list(df.columns)}")

# Show sample data
print("\n📋 Sample Data (first 5 rows):")
print(df.head())

# Convert columns to numeric
df['node_id'] = pd.to_numeric(df['node_id'])
df['soil_moisture'] = pd.to_numeric(df['soil_moisture'])
df['temperature'] = pd.to_numeric(df['temperature'])
df['humidity'] = pd.to_numeric(df['humidity'])

# Check distribution by node_id (crop)
print("\n📊 Distribution by Node (Crop):")
print(df['node_id'].value_counts().sort_index())

# For each node, show moisture range
print("\n📊 Soil Moisture Range per Crop:")
print(df.groupby('node_id')['soil_moisture'].agg(['min', 'max', 'mean', 'count']))