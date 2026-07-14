# Installation Guide — Smart Irrigation and Plant Health Monitoring System

This covers every package/library needed across the four layers in Section
3.8 (Tools and Technologies): Embedded Systems, Data Transmission, Machine
Learning, and Database/Software.

---

## 1. Python packages (all layers, one command)

All Python dependencies — Flask API, pyserial data pipeline, and the
scikit-learn ML stack — are combined in `requirements-all.txt`.

```bash
python3 -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements-all.txt
```

If you only want the Flask backend on its own (e.g. deploying just the API),
use `requirements.txt` instead — it's the same file minus `pyserial` and the
ML packages.

| Package | Layer | Purpose |
|---|---|---|
| Flask | Database/Software | Web framework for the REST API |
| Flask-SQLAlchemy | Database/Software | ORM mapping Python models to MySQL tables |
| Flask-JWT-Extended | Database/Software | JWT auth for the dashboard/users |
| Flask-Cors | Database/Software | Lets the web dashboard call the API cross-origin |
| PyMySQL | Database/Software | Pure-Python MySQL driver used by SQLAlchemy |
| python-dotenv | Database/Software | Loads `.env` config into the app |
| pyserial | IoT/Data Transmission | Reads sensor data off the Arduino's USB serial port |
| pandas | Machine Learning | Cleaning/structuring historical sensor data |
| numpy | Machine Learning | Numerical operations underlying pandas/scikit-learn |
| scikit-learn | Machine Learning | Logistic regression / decision tree / random forest models |
| matplotlib | Machine Learning | Plotting training curves and evaluation charts |
| jupyter | Machine Learning | Notebook environment for model development |

---

## 2. MySQL server

Ubuntu/Debian:

```bash
sudo apt update
sudo apt install mysql-server
sudo mysql_secure_installation
```

macOS (Homebrew):

```bash
brew install mysql
brew services start mysql
```

Windows: install via the [MySQL Installer](https://dev.mysql.com/downloads/installer/).

Once installed, load the schema:

```bash
mysql -u root -p < schema.sql
```

---

## 3. Mosquitto MQTT broker (wireless extension only)

Not required for the current USB/serial prototype. Install this only when
you upgrade to the ESP32 + MQTT data transmission path described in Section
3.5 as the designed extension.

```bash
sudo apt install mosquitto mosquitto-clients
sudo systemctl enable --now mosquitto
```

---

## 4. Arduino IDE libraries

Install the Arduino IDE itself from
[arduino.cc/en/software](https://www.arduino.cc/en/software), then add these
libraries via **Sketch → Include Library → Manage Libraries**:

| Library | Author | Purpose |
|---|---|---|
| DHT sensor library | Adafruit | Reads the DHT22 temperature/humidity sensor |
| Adafruit Unified Sensor | Adafruit | Required dependency of the DHT library |

The soil moisture sensor (analogue) and the 5V relay module (digital output)
use the Arduino core's built-in `analogRead()` / `digitalWrite()` — no extra
library needed.

**Extension path (ESP32 + MQTT):** when you move to wireless transmission,
also install:

| Library | Author | Purpose |
|---|---|---|
| PubSubClient | Nick O'Leary | MQTT publish/subscribe from the ESP32 |
| WiFi (bundled with ESP32 board package) | Espressif | Wi-Fi connectivity |

Install ESP32 board support first via **File → Preferences → Additional
Board Manager URLs** →
`https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`,
then **Tools → Board → Boards Manager** → search "esp32" → install.

---

## 5. Verifying everything installed correctly

```bash
# Python packages
python3 -c "import flask, flask_sqlalchemy, flask_jwt_extended, pymysql, serial, pandas, sklearn; print('Python OK')"

# MySQL
mysql --version

# Mosquitto (only if installed)
mosquitto -h
```
