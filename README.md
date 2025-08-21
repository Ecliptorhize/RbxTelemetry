# RbxTelemetry

A lightweight Python client for batching and sending telemetry events to a
remote HTTP endpoint.  Events are collected locally and can be flushed to the
server in batches.

## Usage

```python
from rbxtelemetry import TelemetryClient

client = TelemetryClient("https://example.com/telemetry")
client.log_event("game_start", {"user": "Alice"})
client.flush()
```
