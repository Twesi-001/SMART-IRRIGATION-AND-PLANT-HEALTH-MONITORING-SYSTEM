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

# ===== ALL NODE IDs =====
# These are the 20 crops your ML model was trained on
ALL_NODE_IDS = list(range(1, 21))  # 1 to 20

# Crop names for display
CROP_NAMES = {
    1: "Maize",
    2: "Tomato",
    3: "Onion",
    4: "Cabbage",
    5: "Mango",
    6: "Banana",
    7: "Pineapple",
    8: "Passion Fruit",
    9: "Carrot",
    10: "Capsicum",
    11: "Eggplant",
    12: "Sukuma Wiki",
    13: "Spinach",
    14: "Beans",
    15: "Garlic",
    16: "Strawberry",
    17: "Lettuce",
    18: "Cucumber",
    19: "Watermelon",
    20: "Pumpkin"
}

# ===== FUNCTIONS =====

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
            crop = CROP_NAMES.get(node_id, f"Node-{node_id}")
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
    """Send the same reading to ALL nodes"""
    print(f"\n📤 Sending to ALL {len(ALL_NODE_IDS)} nodes...")
    
    # Use threading for faster sending
    threads = []
    for node_id in ALL_NODE_IDS:
        thread = threading.Thread(
            target=send_reading,
            args=(moisture, temp, humidity, node_id)
        )
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    print(f"✅ Done! All {len(ALL_NODE_IDS)} nodes updated.")

def main():
    print("🌱 Smart Irrigation Data Ingest")
    print("================================")
    print(f"📡 Connecting to {SERIAL_PORT} at {BAUD_RATE} baud...")
    print(f"📤 Will send data to ALL {len(ALL_NODE_IDS)} nodes")
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
    last_sent = 0
    
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
    print(f"📡 Sending to nodes: {ALL_NODE_IDS}")
    main()