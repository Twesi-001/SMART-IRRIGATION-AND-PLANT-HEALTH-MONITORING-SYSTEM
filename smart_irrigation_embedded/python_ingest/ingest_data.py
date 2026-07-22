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

# ===== FUNCTIONS =====

def get_all_node_ids():
    """Fetch ALL node IDs from the database dynamically"""
    try:
        response = requests.get(
            "https://smart-irrigation-and-plant-health.onrender.com/api/nodes",
            timeout=10
        )
        if response.status_code == 200:
            nodes = response.json()
            node_ids = [node['id'] for node in nodes]
            print(f"📡 Found {len(node_ids)} nodes in database")
            return node_ids
        else:
            print(f"⚠️ Could not fetch nodes: {response.status_code}")
            return list(range(1, 21))
    except Exception as e:
        print(f"⚠️ Error fetching nodes: {e}")
        return list(range(1, 21))

def get_crop_name(node_id):
    """Get crop name for a node (optional, for display)"""
    try:
        response = requests.get(
            f"https://smart-irrigation-and-plant-health.onrender.com/api/nodes/{node_id}",
            timeout=5
        )
        if response.status_code == 200:
            node = response.json()
            return node.get('crop_type', f"Node-{node_id}")
    except:
        pass
    return f"Node-{node_id}"

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
            # Optional: get crop name for display
            crop = get_crop_name(node_id)
            print(f"   ✅ {crop} (Node {node_id}): Soil={data['soil_moisture']}%, Temp={data['temperature']}°C, Hum={data['humidity']}%")
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
    # Get ALL nodes from the database
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