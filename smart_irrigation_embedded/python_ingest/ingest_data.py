import serial # type: ignore
import requests # type: ignore
import time
import re
import threading

# ===== CONFIGURATION =====
API_URL = "https://smart-irrigation-and-plant-health.onrender.com/api/readings"
API_KEY = "PbCg3h3T0NzuNlg7Bq1YBurjIRwBFYS9908eTksmO7g"

# Serial port configuration
SERIAL_PORT = "COM4"  # ← CHANGE THIS TO YOUR PORT
BAUD_RATE = 9600

# ===== AUTH CREDENTIALS =====
AUTH_USERNAME = "testuser"  # ← Change to a valid user
AUTH_PASSWORD = "test123"

# ===== TOKEN (will be fetched automatically) =====
TOKEN = None

# ===== FUNCTIONS =====

def get_token():
    """Login and get a fresh token"""
    global TOKEN
    try:
        response = requests.post(
            "https://smart-irrigation-and-plant-health.onrender.com/api/auth/login",
            json={"username": AUTH_USERNAME, "password": AUTH_PASSWORD},
            timeout=10
        )
        if response.status_code == 200:
            TOKEN = response.json().get("access_token")
            print(f"✅ Token obtained successfully!")
            return TOKEN
        else:
            print(f"⚠️ Failed to get token: {response.status_code}")
            return None
    except Exception as e:
        print(f"⚠️ Error getting token: {e}")
        return None

def get_all_node_ids():
    """Fetch ALL node IDs from the database with authentication"""
    global TOKEN
    
    # If no token, get one
    if not TOKEN:
        get_token()
    
    if not TOKEN:
        print("⚠️ No token available! Using default nodes.")
        return list(range(1, 21))
    
    try:
        response = requests.get(
            "https://smart-irrigation-and-plant-health.onrender.com/api/nodes",
            headers={"Authorization": f"Bearer {TOKEN}"},
            timeout=10
        )
        if response.status_code == 200:
            nodes = response.json()
            node_ids = [node['id'] for node in nodes]
            print(f"📡 Found {len(node_ids)} nodes in database")
            return node_ids
        elif response.status_code == 401:
            # Token expired, try to refresh
            print("⚠️ Token expired. Getting new token...")
            get_token()
            if TOKEN:
                # Retry with new token
                response = requests.get(
                    "https://smart-irrigation-and-plant-health.onrender.com/api/nodes",
                    headers={"Authorization": f"Bearer {TOKEN}"},
                    timeout=10
                )
                if response.status_code == 200:
                    nodes = response.json()
                    node_ids = [node['id'] for node in nodes]
                    print(f"📡 Found {len(node_ids)} nodes in database")
                    return node_ids
            return list(range(1, 21))
        else:
            print(f"⚠️ Could not fetch nodes: {response.status_code}")
            return list(range(1, 21))
    except Exception as e:
        print(f"⚠️ Error fetching nodes: {e}")
        return list(range(1, 21))

def send_reading(moisture, temp, humidity, node_id):
    """Send sensor reading to the API for a specific node"""
    data = {
        "node_id": node_id,
        "soil_moisture": round(moisture, 2),
        "temperature": round(temp, 2),
        "humidity": round(humidity, 2)
    }
    
    try:
        response = requests.post(
            API_URL,
            headers={"X-API-Key": API_KEY},
            json=data,
            timeout=5
        )
        
        if response.status_code == 201:
            print(f"   ✅ Node {node_id}: Soil={data['soil_moisture']}%, Temp={data['temperature']}°C, Hum={data['humidity']}%")
        else:
            print(f"   ❌ Node {node_id}: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Node {node_id}: Connection error")

def extract_values_from_lines(lines):
    """Extract moisture, temp, humidity from a list of lines"""
    moisture = None
    temp = None
    humidity = None
    
    for line in lines:
        match = re.search(r'Soil Moisture:\s*([\d.]+)%', line)
        if match:
            moisture = float(match.group(1))
        
        match = re.search(r'Temperature:\s*([\d.]+)\s*°C', line)
        if match:
            temp = float(match.group(1))
        
        match = re.search(r'Humidity:\s*([\d.]+)%', line)
        if match:
            humidity = float(match.group(1))
    
    if moisture is not None and temp is not None and humidity is not None:
        return {'moisture': moisture, 'temp': temp, 'humidity': humidity}
    return None

def send_to_all_nodes(moisture, temp, humidity):
    """Send the same reading to ALL nodes in the database"""
    # Get ALL nodes from the database with auth
    node_ids = get_all_node_ids()
    
    if not node_ids:
        print("⚠️ No nodes found!")
        return
    
    print(f"\n📤 Sending to ALL {len(node_ids)} nodes...")
    
    # Use threading for faster sending
    threads = []
    for node_id in node_ids:
        thread = threading.Thread(
            target=send_reading,
            args=(moisture, temp, humidity, node_id)
        )
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    print(f"✅ Done! All {len(node_ids)} nodes updated.")

def main():
    print("🌱 Smart Irrigation Data Ingest")
    print("================================")
    print(f"📡 Connecting to {SERIAL_PORT} at {BAUD_RATE} baud...")
    print("-" * 40)
    
    # Get initial token
    print("🔑 Getting authentication token...")
    get_token()
    
    if not TOKEN:
        print("❌ Failed to get token. Please check credentials.")
        return
    
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print("✅ Connected!")
        time.sleep(2)
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    print("📊 Waiting for sensor data... Press Ctrl+C to stop")
    print("=" * 40)
    
    buffer = []
    
    while True:
        try:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print(f"📥 {line}")
                buffer.append(line)
                
                if "SENSOR READINGS" in line:
                    data = extract_values_from_lines(buffer)
                    if data:
                        send_to_all_nodes(
                            data['moisture'],
                            data['temp'],
                            data['humidity']
                        )
                    buffer = []
                    
        except KeyboardInterrupt:
            print("\n🛑 Stopped by user")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
        
        time.sleep(0.1)

if __name__ == "__main__":
    main()