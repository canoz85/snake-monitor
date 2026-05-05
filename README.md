# snake-monitor

Monitor your **Snake** game, **snake-brain (DQN)**, and **llm-brain** components in real-time using FUXA and an OPC UA gateway.

```
snake / snake-brain / llm-brain
        │  HTTP POST /tags
        ▼
   gateway (Python)          ← port 8080  (HTTP update API)
        │  OPC UA Server
        ▼
   FUXA (Windows)            ← port 4840  (OPC UA client)
        │
        ▼
   Dashboard (browser)
```

---

## Repository layout

```
snake-monitor/
├── gateway/                 # Python OPC UA server + HTTP REST API
│   ├── opcua_gateway.py     # Main gateway script (run this)
│   ├── requirements.txt     # pip dependencies
│   └── README.md            # Gateway-specific instructions
├── fuxa/                    # FUXA project export
│   ├── SnakeMonitor.json    # Import this into FUXA
│   └── README.md            # FUXA import / usage guide
└── README.md                # ← you are here
```

---

## Prerequisites

| Software | Version | Install |
|----------|---------|---------|
| Python | 3.10 + | https://www.python.org/downloads/windows/ |
| FUXA | latest | https://github.com/frangoteam/FUXA (Windows installer or `npm start`) |

FUXA and Python must run on the same Windows machine (or you can change `localhost` to the gateway IP in FUXA settings).

---

## Quick start (Windows)

### Step 1 – Install Python dependencies

Open **Command Prompt**, navigate to the `gateway/` folder, then run:

```bat
cd gateway
pip install -r requirements.txt
```

### Step 2 – Start the gateway

```bat
python opcua_gateway.py
```

Expected output:

```
INFO  HTTP API starting on http://0.0.0.0:8080
INFO  OPC UA server listening on opc.tcp://0.0.0.0:4840/snake-monitor/
INFO  OPC UA node created: ns=2;s=snake.score
INFO  OPC UA node created: ns=2;s=snake.alive
...
```

Leave this window open. The gateway exposes:

| Service | URL / Port | Purpose |
|---------|-----------|---------|
| OPC UA server | `opc.tcp://localhost:4840/snake-monitor/` | FUXA reads tags here |
| HTTP API | `http://localhost:8080/tags` | Components push updates here |

### Step 3 – Import the FUXA project

1. Open FUXA in your browser (`http://localhost:1881` by default).
2. Click the menu icon → **Load project**.
3. Select `fuxa/SnakeMonitor.json`.
4. The Dashboard view opens with 6 live panels and a score chart.

### Step 4 – Connect FUXA to the gateway

After import, FUXA should auto-connect. Verify:

1. Sidebar → **Devices** → **SnakeOPCUA** should show a green indicator.
2. If not: edit the device, confirm the endpoint is `opc.tcp://localhost:4840/snake-monitor/`, security = **None**, auth = **Anonymous**, then save.

### Step 5 – Push metrics from your components

Any component (C++, Python, etc.) posts a JSON body to the gateway HTTP API:

```bash
curl -X POST http://localhost:8080/tags \
     -H "Content-Type: application/json" \
     -d "{\"snake.score\": 42, \"snake.alive\": true, \"dqn.epsilon\": 0.05}"
```

**Python example:**

```python
import requests

requests.post("http://localhost:8080/tags", json={
    "snake.score": 15,
    "snake.alive": True,
    "dqn.epsilon": 0.08,
    "llm.mode": "assist",
})
```

**C++ (libcurl) example:**

```cpp
// POST to http://localhost:8080/tags
// Content-Type: application/json
// Body: {"snake.score":42,"dqn.epsilon":0.03,"llm.mode":"assist"}
```

---

## Monitored tags

| Tag | Type | Default | Description |
|-----|------|---------|-------------|
| `snake.score` | Int64 | 0 | Current game score |
| `snake.alive` | Boolean | true | Snake is alive |
| `dqn.epsilon` | Double | 1.0 | Exploration rate |
| `dqn.reward_last` | Double | 0.0 | Last episode reward |
| `llm.mode` | String | "off" | LLM assist mode |
| `system.latency_ms` | Int64 | 0 | Round-trip latency |

---

## Firewall note

If FUXA and the gateway are on the **same machine**, no firewall changes are needed.

If they run on different machines, allow inbound TCP on **port 4840** (OPC UA) and **port 8080** (HTTP API) in Windows Defender Firewall.

---

## More details

- [`gateway/README.md`](gateway/README.md) – gateway installation and HTTP API reference.
- [`fuxa/README.md`](fuxa/README.md) – FUXA import steps and dashboard customisation.
