# Smart Irrigation — Database & Flask REST API

This is the Database and Software Development layer (Section 3.7) of the Smart
Irrigation and Plant Health Monitoring System. It provides:

- A normalized (3NF) MySQL schema — `schema.sql`
- A Flask REST API (`app/`) that the pyserial data-logging script, the
  scikit-learn ML script, and the web dashboard all talk to

## 1. Set up MySQL

```bash
mysql -u root -p < schema.sql
```

This creates the `smart_irrigation` database, all six tables, and seeds one
sensor node (`id = 1`) so you can start posting readings immediately.

Then create a dedicated DB user (recommended over using root):

```sql
CREATE USER 'irrigation_user'@'localhost' IDENTIFIED BY 'change_me';
GRANT ALL PRIVILEGES ON smart_irrigation.* TO 'irrigation_user'@'localhost';
FLUSH PRIVILEGES;
```

## 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your real DB credentials and generate random values for
`FLASK_SECRET_KEY`, `JWT_SECRET_KEY`, and `INGEST_API_KEY` (e.g. `python3 -c
"import secrets; print(secrets.token_hex(32))"`).

## 3. Install dependencies and run

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 run.py
```

The API runs at `http://localhost:5000`.

## Authentication model

There are two separate auth mechanisms:

- **User JWT** (`Authorization: Bearer <token>`) — for the farmer/extension
  officer dashboard. Get a token from `POST /api/auth/login`. Used for manual
  pump commands and resolving alerts.
- **Device API key** (`X-API-Key: <INGEST_API_KEY>`) — for the Arduino's
  pyserial host script and the ML inference script, which aren't logged-in
  users. Used for posting readings, predictions, alerts, and auto pump
  commands.

## Endpoint reference

| Method | Endpoint | Auth | Purpose |
|---|---|---|---|
| GET | `/api/health` | none | Health check |
| POST | `/api/auth/register` | none | Create a user account |
| POST | `/api/auth/login` | none | Log in, get a JWT |
| GET | `/api/nodes` | none | List sensor nodes |
| POST | `/api/nodes` | JWT | Register a new sensor node |
| POST | `/api/readings` | API key | Ingest a sensor reading |
| GET | `/api/readings/live?node_id=1` | none | Most recent reading |
| GET | `/api/readings/history?node_id=1&limit=100&start=&end=` | none | Historical readings |
| POST | `/api/predictions` | API key | Submit an ML prediction for a reading |
| GET | `/api/predictions/latest?node_id=1` | none | Latest prediction |
| GET | `/api/predictions/history?node_id=1` | none | Prediction history |
| POST | `/api/pump/command` | JWT | Manual pump override |
| POST | `/api/pump/auto-command` | API key | Log an automatic pump action |
| GET | `/api/pump/status?node_id=1` | none | Current/last pump state |
| GET | `/api/pump/history?node_id=1` | none | Pump command log |
| GET | `/api/alerts?node_id=1&resolved=false` | none | List alerts |
| POST | `/api/alerts` | API key | Raise an alert |
| POST | `/api/alerts/<id>/resolve` | JWT | Mark an alert resolved |

## Example requests

Register and log in:

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "farmer1", "password": "pass123", "role": "farmer"}'

curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "farmer1", "password": "pass123"}'
```

Post a sensor reading (from the pyserial script):

```bash
curl -X POST http://localhost:5000/api/readings \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <INGEST_API_KEY>" \
  -d '{"node_id": 1, "soil_moisture": 22.5, "temperature": 27.1, "humidity": 60.0}'
```

Manual pump override from the dashboard:

```bash
curl -X POST http://localhost:5000/api/pump/command \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"node_id": 1, "command": "ON"}'
```

## Design notes matching the proposal

- Schema is normalized to 3NF as stated in Section 3.7: predictions reference
  the specific reading they were computed from, and pump commands reference
  the user who issued a manual override, avoiding repeated/redundant data.
- `sensor_nodes` exists even though the prototype has one node, so the system
  can scale to a multi-zone deployment (Section 3.10, limitation 4) without a
  schema redesign.
- The device API key pattern lets the embedded/edge scripts push data without
  needing full user accounts, while the dashboard-facing endpoints use JWT,
  matching the "secured where appropriate using JSON Web Token
  authentication" note in Section 3.7.
- `POST /api/pump/auto-command` and `POST /api/alerts` give the ML/threshold
  logic a place to log automatic decisions, which the dashboard can then
  read back via the `GET` endpoints.

## Tested

All endpoints were smoke-tested end-to-end (register → login → ingest
reading → live/history reads → submit prediction → manual pump command →
pump status → raise alert → resolve alert) against an in-memory database
before delivery.
