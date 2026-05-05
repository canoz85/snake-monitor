"""
Snake Monitor – OPC UA Gateway
===============================
Runs two services in one process:
  • An OPC UA server  (port 4840)  – FUXA connects here as OPC UA Client
  • An HTTP REST API  (port 8080)  – snake / snake-brain / llm-brain POST updates here

Usage
-----
    pip install -r requirements.txt
    python opcua_gateway.py

Then in a second terminal (optional – confirms the HTTP API works):
    curl http://localhost:8080/tags
    curl -X POST http://localhost:8080/tags ^
         -H "Content-Type: application/json" ^
         -d "{\"snake.score\": 5, \"dqn.epsilon\": 0.2, \"llm.mode\": \"assist\"}"
"""

import asyncio
import logging
import threading
from typing import Any, Dict

import uvicorn
from asyncua import Server, ua
from fastapi import FastAPI

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
OPCUA_ENDPOINT = "opc.tcp://0.0.0.0:4840/snake-monitor/"
OPCUA_NAMESPACE_URI = "urn:snake-monitor:opcua"

HTTP_HOST = "0.0.0.0"
HTTP_PORT = 8080

OPCUA_UPDATE_INTERVAL = 0.2  # seconds between OPC UA write cycles (5 Hz)

# ---------------------------------------------------------------------------
# Shared tag store – updated by HTTP API, read by OPC UA writer loop
# ---------------------------------------------------------------------------
TAGS: Dict[str, Any] = {
    "snake.score": 0,
    "snake.alive": True,
    "dqn.epsilon": 1.0,
    "dqn.reward_last": 0.0,
    "llm.mode": "off",
    "system.latency_ms": 0,
}

# Protects TAGS dict for concurrent HTTP + asyncio access
_tags_lock = threading.Lock()

# ---------------------------------------------------------------------------
# HTTP API (FastAPI / uvicorn)
# ---------------------------------------------------------------------------
app = FastAPI(title="Snake Monitor Gateway", version="1.0.0")


@app.get("/tags", summary="Return all current tag values")
def get_tags() -> Dict[str, Any]:
    with _tags_lock:
        return dict(TAGS)


@app.post("/tags", summary="Update one or more tag values")
def update_tags(payload: Dict[str, Any]) -> Dict[str, Any]:
    with _tags_lock:
        for key, value in payload.items():
            if key in TAGS:
                TAGS[key] = value
    return {"ok": True, "updated": list(payload.keys())}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
log = logging.getLogger("gateway")


def _ua_variant(value: Any) -> ua.Variant:
    """Convert a Python value to the matching OPC UA Variant type."""
    if isinstance(value, bool):
        return ua.Variant(value, ua.VariantType.Boolean)
    if isinstance(value, int) and not isinstance(value, bool):
        return ua.Variant(value, ua.VariantType.Int64)
    if isinstance(value, float):
        return ua.Variant(value, ua.VariantType.Double)
    return ua.Variant(str(value), ua.VariantType.String)


# ---------------------------------------------------------------------------
# OPC UA server (asyncio)
# ---------------------------------------------------------------------------
async def opcua_server_task() -> None:
    server = Server()
    await server.init()
    server.set_endpoint(OPCUA_ENDPOINT)
    server.set_server_name("Snake Monitor OPC UA Gateway")

    # Anonymous / no security (compatible with FUXA default OPC UA plugin)
    server.set_security_policy([ua.SecurityPolicyType.NoSecurity])

    idx = await server.register_namespace(OPCUA_NAMESPACE_URI)

    objects = server.nodes.objects
    root_node = await objects.add_object(idx, "SnakeMonitor")

    # Create one OPC UA variable per tag
    opc_vars: Dict[str, Any] = {}
    with _tags_lock:
        snapshot = dict(TAGS)

    for name, value in snapshot.items():
        node = await root_node.add_variable(idx, name, _ua_variant(value))
        await node.set_writable()
        opc_vars[name] = node
        log.info("OPC UA node created: ns=%d;s=%s", idx, name)

    log.info("OPC UA server listening on %s", OPCUA_ENDPOINT)

    async with server:
        while True:
            with _tags_lock:
                snapshot = dict(TAGS)
            for name, node in opc_vars.items():
                await node.write_value(_ua_variant(snapshot[name]))
            await asyncio.sleep(OPCUA_UPDATE_INTERVAL)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def _run_http() -> None:
    """Run FastAPI/uvicorn in a background daemon thread."""
    uvicorn.run(app, host=HTTP_HOST, port=HTTP_PORT, log_level="info")


def main() -> None:
    # Start HTTP server in a daemon thread so it exits when the main process exits
    http_thread = threading.Thread(target=_run_http, daemon=True, name="http-api")
    http_thread.start()
    log.info("HTTP API starting on http://%s:%d", HTTP_HOST, HTTP_PORT)

    # Run OPC UA server on the main asyncio event loop
    asyncio.run(opcua_server_task())


if __name__ == "__main__":
    main()
