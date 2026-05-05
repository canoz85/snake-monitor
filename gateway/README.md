# Gateway – Python OPC UA Server

This folder contains the monitoring gateway for the snake-monitor project.

## What it does

| Service | Port | Purpose |
|---------|------|---------|
| OPC UA server | **4840** | FUXA connects here to read live tag values |
| HTTP REST API | **8080** | snake / snake-brain / llm-brain push updates here |

## Exposed tags

| Tag | Type | Default | Description |
|-----|------|---------|-------------|
| `snake.score` | Int64 | 0 | Current game score |
| `snake.alive` | Boolean | true | Snake alive status |
| `dqn.epsilon` | Double | 1.0 | DQN exploration rate |
| `dqn.reward_last` | Double | 0.0 | Last episode reward |
| `llm.mode` | String | "off" | LLM assist mode |
| `system.latency_ms` | Int64 | 0 | Round-trip latency (ms) |

## Quick start (Windows)

### 1. Install Python 3.10 or newer
Download from https://www.python.org/downloads/windows/

### 2. Install dependencies
Open a Command Prompt in this folder and run:
```bat
pip install -r requirements.txt
```

### 3. Start the gateway
```bat
python opcua_gateway.py
```

You should see:
```
INFO  HTTP API starting on http://0.0.0.0:8080
INFO  OPC UA server listening on opc.tcp://0.0.0.0:4840/snake-monitor/
INFO  OPC UA node created: ns=2;s=snake.score
...
```

### 4. Test the HTTP API (optional)
Open a second Command Prompt:
```bat
curl http://localhost:8080/tags

curl -X POST http://localhost:8080/tags ^
     -H "Content-Type: application/json" ^
     -d "{\"snake.score\": 42, \"snake.alive\": true, \"dqn.epsilon\": 0.05}"
```

## How brains publish metrics

Any component (C++, Python, etc.) can push updates with a simple HTTP POST:

**URL:** `POST http://<gateway-host>:8080/tags`  
**Body:** JSON object with one or more tag names as keys.

### Python example
```python
import requests

requests.post("http://localhost:8080/tags", json={
    "snake.score": 15,
    "snake.alive": True,
})
```

### C++ example (libcurl pseudo-code)
```cpp
std::string body = R"({"snake.score":15,"dqn.epsilon":0.03})";
// HTTP POST body to http://localhost:8080/tags
// Content-Type: application/json
```

## Firewall note (Windows)

If FUXA or the brains run on different machines, allow inbound TCP on port **4840** and **8080** in Windows Defender Firewall.  
For a single-machine setup (FUXA + gateway on the same PC) no firewall changes are needed.
