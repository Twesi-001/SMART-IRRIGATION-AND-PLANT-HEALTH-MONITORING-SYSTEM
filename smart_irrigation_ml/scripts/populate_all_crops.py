import requests # type: ignore
import random
import time
from requests.adapters import HTTPAdapter # type: ignore
from urllib3.util.retry import Retry # type: ignore

# Your live API endpoint
API_URL = "https://smart-irrigation-and-plant-health.onrender.com/api/readings"
API_KEY = "PbCg3h3T0NzuNlg7Bq1YBurjIRwBFYS9908eTksmO7g"

# All crop node IDs
CROP_NODES = list(range(1, 21))  # 1 to 20

# Create a session with retry logic
session = requests.Session()
retry = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry)
session.mount('https://', adapter)

def generate_reading(node_id):
    """Generate realistic sensor readings"""
    # Random soil moisture between 15-80%
    soil_moisture = round(random.uniform(15, 80), 1)
    
    # Temperature: 15-40°C
    temperature = round(random.uniform(15, 40), 1)
    
    # Humidity: 20-90%
    humidity = round(random.uniform(20, 90), 1)
    
    return {
        "node_id": node_id,
        "soil_moisture": soil_moisture,
        "temperature": temperature,
        "humidity": humidity
    }

print("🌱 Generating and posting readings for ALL 20 crops...")
print("📡 Sending to:", API_URL)
print("-" * 50)

total_success = 0
total_fail = 0

for node_id in CROP_NODES:
    print(f"\n📊 Processing Node {node_id}...")
    
    success_count = 0
    fail_count = 0
    
    # Generate 150 readings per crop (3000 total)
    for i in range(150):
        data = generate_reading(node_id)
        
        try:
            response = session.post(
                API_URL, 
                json=data, 
                headers={"X-API-Key": API_KEY},
                timeout=30
            )
            
            if response.status_code == 201:
                success_count += 1
                if (i + 1) % 30 == 0:
                    print(f"   ✅ [{i+1}/150] Node {node_id}: Soil={data['soil_moisture']}%, Temp={data['temperature']}°C")
            else:
                fail_count += 1
                print(f"   ❌ [{i+1}/150] Error: {response.text}")
                
        except Exception as e:
            fail_count += 1
            print(f"   ❌ [{i+1}/150] Connection error: {e}")
        
        time.sleep(0.15)
    
    total_success += success_count
    total_fail += fail_count
    print(f"   📊 Node {node_id}: {success_count} posted, {fail_count} failed")

print("-" * 50)
print(f"\n✅ Done!")
print(f"   ✅ Successfully posted: {total_success} readings")
print(f"   ❌ Failed: {total_fail} readings")
print(f"   🌱 Total crops: 20")
print(f"   📊 Total readings: ~3000")