"""
analytics_client.py

The main application's client for the Analytics service (see analytics/).

Every call is best-effort: if the service is slow or down, the app keeps
working. Variant lookups fall back to a caller-supplied default; event logging
is fire-and-forget on a background thread.

Config (env vars):
    ANALYTICS_URL      base URL of the service   (default http://localhost:8000)
    ANALYTICS_TIMEOUT  per-request timeout, secs (default 0.5)
"""

import json
import os
import threading
import urllib.parse
import urllib.request
from datetime import datetime

ANALYTICS_URL = os.environ.get("ANALYTICS_URL", "http://localhost:8000").rstrip("/")
_TIMEOUT = float(os.environ.get("ANALYTICS_TIMEOUT", "0.5"))


def get_variant(test_name, visitor_id, default=None):
    """
    Return the variant `visitor_id` is assigned for `test_name`.

    Blocks on the Analytics service (short timeout). Returns `default` on any
    error so a rendering path never fails because Analytics is unavailable.
    """
    query = urllib.parse.urlencode({"test": test_name, "visitor": visitor_id or ""})
    url = f"{ANALYTICS_URL}/variant?{query}"
    try:
        with urllib.request.urlopen(url, timeout=_TIMEOUT) as resp:
            return json.loads(resp.read()).get("variant") or default
    except Exception:
        return default


def log_event(event, test_name, visitor_id, variant=None):
    """
    Record an impression or conversion. Non-blocking: the POST runs on a daemon
    thread and any error is swallowed. If `variant` is omitted, the Analytics
    service derives it from the visitor id.
    """
    payload = json.dumps({
        "event": event,
        "test": test_name,
        "visitor": visitor_id,
        "variant": variant,
        "timestamp": datetime.now().isoformat(),
    }).encode()
    threading.Thread(
        target=_post, args=(f"{ANALYTICS_URL}/events", payload), daemon=True
    ).start()


def _post(url, payload):
    try:
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=_TIMEOUT).close()
    except Exception:
        pass
