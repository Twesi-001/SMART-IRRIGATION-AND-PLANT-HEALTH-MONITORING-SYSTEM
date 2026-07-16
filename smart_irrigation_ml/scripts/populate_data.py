import requests # type: ignore
import random
import time
from datetime import datetime
from requests.adapters import HTTPAdapter # type: ignore
from urllib3.util.retry import Retry # type: ignore

# Your live API endpoint
API_URL = "https://smart-irrigation-and-plant-health.onrender.com/api/readings"
API_KEY = "PbCg3h3T0NzuNlg7Bq1YBurjIRwBFYS9908eTksmO7g"

# Create a session with retry logic
session = requests.Session()
retry = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry)
session.mount('https://', adapter)

def generate_reading():
    """Generate realistic sensor readings"""
    # Soil moisture: 15-80% (typical range for agricultural soil)
    soil_moisture = round(random.uniform(15, 80), 1)
    
    # Temperature: 15-40°C (Uganda range)
    temperature = round(random.uniform(15, 40), 1)
    
    # Humidity: 20-90%
    humidity = round(random.uniform(20, 90), 1)
    
    return {
        "node_id": 1,
        "soil_moisture": soil_moisture,
        "temperature": temperature,
        "humidity": humidity
    }

print("🌱 Generating and posting 10,000 synthetic readings...")
print("📡 Sending to:", API_URL)
print("⏳ This will take approximately 10-15 minutes...")
print("-" * 50)

success_count = 0
fail_count = 0
batch_size = 100

for i in range(10000):
    data = generate_reading()
    
    try:
        response = session.post(
            API_URL, 
            json=data, 
            headers={"X-API-Key": API_KEY},
            timeout=30
        )
        
        if response.status_code == 201:
            success_count += 1
            if (i + 1) % 100 == 0:  # Print every 100 records
                print(f"✅ [{i+1}/10000] Posted: Soil={data['soil_moisture']}%, Temp={data['temperature']}°C, Hum={data['humidity']}%")
        else:
            fail_count += 1
            print(f"❌ [{i+1}/10000] Error: {response.text}")
            
    except Exception as e:
        fail_count += 1
        print(f"❌ [{i+1}/10000] Connection error: {e}")
    
    # Small delay to avoid rate limiting
    time.sleep(0.2)

print("-" * 50)
print(f"\n✅ Done!")
print(f"   ✅ Successfully posted: {success_count} readings")
print(f"   ❌ Failed: {fail_count} readings")
print(f"   📊 Total: {success_count + fail_count} attempts")