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

# ===== NODE CACHE (Auto-Discovery) =====
NODE_IDS = []
LAST_FETCH_TIME = 0
FETCH_INTERVAL = 60  # Check for new nodes every 60 seconds

# ===== AUTH CREDENTIALS (kept as backup) =====
AUTH_USERNAME = "testuser"
AUTH_PASSWORD = "test123"

# ===== TOKEN (kept as backup) =====
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

def get_all_node_ids_with_token():
    """Fallback: Fetch nodes using token"""
    global TOKEN
    
    if not TOKEN:
        get_token()
    
    if not TOKEN:
        return list(range(1, 21))
    
    try:
        response = requests.get(
            "https://smart-irrigation-and-plant-health.onrender.com/api/nodes",
            headers={"Authorization": f"Bearer {TOKEN}"},
            timeout=10
        )
        if response.status_code == 200:
            nodes = response.json()
            # ✅ Only use nodes 1-20
            return [node['id'] for node in nodes if 1 <= node['id'] <= 20]
    except:
        pass
    return list(range(1, 21))

def fetch_all_nodes():
    """Fetch ALL node IDs using API key (bypasses user filtering)"""
    global NODE_IDS, LAST_FETCH_TIME
    
    try:
        response = requests.get(
            "https://smart-irrigation-and-plant-health.onrender.com/api/nodes",
            headers={"X-API-Key": API_KEY},
            timeout=10
        )
        if response.status_code == 200:
            nodes = response.json()
            # ✅ ONLY use nodes 1-20 (fixed nodes)
            NODE_IDS = [node['id'] for node in nodes if 1 <= node['id'] <= 20]
            LAST_FETCH_TIME = time.time()
            print(f"📡 Found {len(NODE_IDS)} nodes in database (1-20 only)")
            print(f"📡 Node IDs: {NODE_IDS}")
            return NODE_IDS
        else:
            print(f"⚠️ Could not fetch nodes with API key: {response.status_code}")
            # ✅ Fallback: Use hardcoded nodes 1-20
            NODE_IDS = list(range(1, 21))
            LAST_FETCH_TIME = time.time()
            print(f"📡 Using fallback: nodes 1-20")
            return NODE_IDS
    except Exception as e:
        print(f"⚠️ Error fetching nodes: {e}")
        # ✅ Fallback: Use hardcoded nodes 1-20
        NODE_IDS = list(range(1, 21))
        LAST_FETCH_TIME = time.time()
        print(f"📡 Using fallback: nodes 1-20")
        return NODE_IDS

def get_all_node_ids():
    """Get all node IDs, refreshing cache if needed"""
    global NODE_IDS, LAST_FETCH_TIME
    
    # If we haven't fetched yet, or it's been more than FETCH_INTERVAL seconds
    if not NODE_IDS or (time.time() - LAST_FETCH_TIME) > FETCH_INTERVAL:
        print("🔄 Refreshing node list...")
        return fetch_all_nodes()
    
    return NODE_IDS

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
            return True
        else:
            print(f"   ❌ Node {node_id}: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Node {node_id}: Connection error")
        return False

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
    # Get ALL nodes (auto-refreshes every 60 seconds)
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
    print("🌱 Smart Irrigation Data Ingest (Auto-Discovery Mode)")
    print("=" * 50)
    print(f"📡 Connecting to {SERIAL_PORT} at {BAUD_RATE} baud...")
    print("🔄 Will auto-discover new nodes every 60 seconds")
    print("-" * 50)
    
    # Initial fetch of all nodes
    print("🔑 Fetching all nodes from database...")
    fetch_all_nodes()
    
    if not NODE_IDS:
        print("⚠️ No nodes found! Will keep checking...")
    
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print("✅ Connected to Arduino!")
        time.sleep(2)
    except Exception as e:
        print(f"❌ Error connecting to serial port: {e}")
        return
    
    print("📊 Waiting for sensor data... Press Ctrl+C to stop")
    print("=" * 50)
    
    buffer = []
    reading_count = 0
    
    while True:
        try:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print(f"📥 {line}")
                buffer.append(line)
                
                if "SENSOR READINGS" in line:
                    data = extract_values_from_lines(buffer)
                    if data:
                        reading_count += 1
                        print(f"\n📊 Reading #{reading_count}:")
                        print(f"   💧 Moisture: {data['moisture']}%")
                        print(f"   🌡️ Temperature: {data['temp']}°C")
                        print(f"   💨 Humidity: {data['humidity']}%")
                        
                        # Send to ALL nodes (auto-discovers new ones)
                        send_to_all_nodes(
                            data['moisture'],
                            data['temp'],
                            data['humidity']
                        )
                    buffer = []
                    
        except KeyboardInterrupt:
            print("\n" + "=" * 50)
            print(f"🛑 Stopped by user")
            print(f"📊 Total readings sent: {reading_count}")
            print("=" * 50)
            break
        except Exception as e:
            print(f"❌ Error: {e}")
        
        time.sleep(0.1)

if __name__ == "__main__":
    main()