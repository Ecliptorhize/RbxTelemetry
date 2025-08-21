"""Telemetry client for sending events to a server.

This module exposes :class:`TelemetryClient` which collects events and sends
them to a remote HTTP endpoint.  It keeps a local queue so events can be
batched via :meth:`flush`.
"""

from __future__ import annotations

import time
import uuid
from typing import Callable, Dict, List, Optional, Any


Sender = Callable[[str, Dict[str, Any]], None]


class TelemetryClient:
    """Collects and sends telemetry events.

    Parameters
    ----------
    server_url:
        Endpoint where events will be POSTed as JSON.
    session_id:
        Optional identifier for the current session.  One will be generated
        automatically if not provided.
    sender:
        Optional callable used to transmit events.  Defaults to a small wrapper
        around :func:`requests.post`.  This is mainly to ease testing since a
        custom sender can be injected.
    """

    def __init__(
        self,
        server_url: str,
        *,
        session_id: Optional[str] = None,
        sender: Optional[Sender] = None,
    ) -> None:
        self.server_url = server_url
        self.session_id = session_id or str(uuid.uuid4())
        self._sender: Sender = sender or self._default_sender
        self._queue: List[Dict[str, Any]] = []

    def log_event(self, name: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Add an event to the queue.

        Parameters
        ----------
        name:
            Name of the event.
        data:
            Optional mapping with extra information for the event.
        """
        event = {
            "name": name,
            "timestamp": time.time(),
            "data": data or {},
        }
        self._queue.append(event)

    def flush(self) -> int:
        """Send queued events to the server.

        Returns
        -------
        int
            The number of events that were transmitted.
        """
        if not self._queue:
            return 0

        payload = {"session_id": self.session_id, "events": self._queue}
        self._sender(self.server_url, payload)
        sent = len(self._queue)
        self._queue = []
        return sent

    @staticmethod
    def _default_sender(url: str, payload: Dict[str, Any]) -> None:
        """Send the payload using :mod:`requests`.

        Network errors are intentionally swallowed since telemetry should not
        disrupt the main application flow.
        """
        try:
            import requests

            requests.post(url, json=payload, timeout=5)
        except Exception:
            pass
