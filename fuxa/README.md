# FUXA Project – SnakeMonitor

`SnakeMonitor.json` is a ready-to-import FUXA project that:

- Defines an **OPC UA Client device** pointing to the Python gateway.
- Pre-creates **6 tags** bound to the gateway's OPC UA nodes.
- Includes a **dark-themed SVG dashboard** with live value displays and a score trend chart.

## Tags pre-configured

| Tag ID | OPC UA Node | Type | Description |
|--------|-------------|------|-------------|
| `t_snake_score` | `ns=2;s=snake.score` | Int64 | Current game score |
| `t_snake_alive` | `ns=2;s=snake.alive` | Boolean | Snake alive flag |
| `t_dqn_epsilon` | `ns=2;s=dqn.epsilon` | Double | DQN epsilon (exploration) |
| `t_dqn_reward` | `ns=2;s=dqn.reward_last` | Double | Last DQN episode reward |
| `t_llm_mode` | `ns=2;s=llm.mode` | String | LLM assist mode |
| `t_sys_latency` | `ns=2;s=system.latency_ms` | Int64 | Round-trip latency (ms) |

## How to import into FUXA

1. **Start the gateway first** (see `gateway/README.md`).
2. Open FUXA in your browser (default: `http://localhost:1881`).
3. Click the **FUXA** menu icon → **Load project**.
4. Select `fuxa/SnakeMonitor.json` and confirm.
5. FUXA will load the device, tags, and dashboard view.

## Connect the OPC UA device

After import, FUXA should automatically connect to the gateway. If it does not:

1. Go to **Devices** in the sidebar.
2. Select **SnakeOPCUA** → click **Edit**.
3. Verify the endpoint: `opc.tcp://localhost:4840/snake-monitor/`
4. Security: **None** / Authentication: **Anonymous**.
5. Click **Save** – the device should turn green (connected).

## Add more widgets (optional)

The dashboard comes with pre-built value panels and a score chart.
To add or customise:

1. Click the **pencil (edit)** icon on the Dashboard view.
2. Use the **Shapes** / **HTML Controls** toolbar to add gauges, switches, etc.
3. Right-click a gauge → **Property** → bind it to one of the pre-created tags.
4. Click **Save** when finished.
