import pandas as pd # type: ignore
import os

# Load the data
csv_path = '../data/raw/training_data_all_crops.csv'
df = pd.read_csv(csv_path, sep='\t')
print(f"✅ Loaded {len(df)} readings")

# Clean columns
df.columns = df.columns.str.strip()
df['node_id'] = pd.to_numeric(df['node_id'])
df['soil_moisture'] = pd.to_numeric(df['soil_moisture'])
df['temperature'] = pd.to_numeric(df['temperature'])
df['humidity'] = pd.to_numeric(df['humidity'])

# Show current distribution
print("\n📊 Current Distribution:")
print(df['node_id'].value_counts().sort_index())

# Balance: Reduce Node 1 to 300 readings
print("\n⚖️ Balancing data...")

# For each node, sample 300 readings (or less if not enough)
balanced_dfs = []
for node_id in df['node_id'].unique():
    node_data = df[df['node_id'] == node_id]
    
    # If more than 300, sample 300
    if len(node_data) > 300:
        sampled = node_data.sample(n=300, random_state=42)
    else:
        sampled = node_data
    
    balanced_dfs.append(sampled)
    print(f"   Node {node_id}: {len(node_data)} → {len(sampled)} readings")

# Combine all balanced data
balanced_df = pd.concat(balanced_dfs, ignore_index=True)

# Shuffle
balanced_df = balanced_df.sample(frac=1, random_state=42).reset_index(drop=True)

print(f"\n✅ Balanced dataset: {len(balanced_df)} readings")

# Show new distribution
print("\n📊 New Distribution:")
print(balanced_df['node_id'].value_counts().sort_index())

# Save balanced data
output_path = '../data/processed/training_data_balanced_all_crops.csv'
balanced_df.to_csv(output_path, index=False)
print(f"\n✅ Saved to: {output_path}")