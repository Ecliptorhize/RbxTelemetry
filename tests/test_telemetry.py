from rbxtelemetry import TelemetryClient


def test_log_and_flush():
    sent_payloads = []

    def sender(url, payload):
        sent_payloads.append((url, payload))

    client = TelemetryClient("https://example.com/telemetry", sender=sender)
    client.log_event("start", {"user": "Bob"})

    assert len(client._queue) == 1
    sent = client.flush()
    assert sent == 1
    assert len(client._queue) == 0

    assert sent_payloads[0][0] == "https://example.com/telemetry"
    payload = sent_payloads[0][1]
    assert payload["session_id"]
    events = payload["events"]
    assert events[0]["name"] == "start"
    assert events[0]["data"] == {"user": "Bob"}
