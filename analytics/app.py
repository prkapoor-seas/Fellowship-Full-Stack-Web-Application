"""
Analytics service -- HTTP API for A/B testing.

This is one of the two backend services (the other is the main Flask
application). It owns ab_tests.json and the ab_events.sqlite event store; the
main app talks to it over HTTP via analytics_client.py.

Endpoints:
    GET  /healthz             liveness / readiness probe
    GET  /variant             ?test=<name>&visitor=<id>  -> {"test", "variant"}
    GET  /variants            ?visitor=<id>              -> {test: variant, ...}
    POST /events              {event, test, visitor, variant?, timestamp?}
    GET  /metrics/<test>      per-variant conversion summary

Run locally:   python -m analytics.app        (or: gunicorn analytics.app:app)
"""

import os
from datetime import datetime
from html import escape

from flask import Flask, jsonify, request

from analytics import assign, store

app = Flask(__name__)

_DASH_ROW = """
    <tr><td>{variant}</td><td>{impressions}</td><td>{actions}</td>
        <td>{rate:.1%}</td></tr>"""


@app.get("/")
def dashboard():
    """Human-readable overview of every running test and its live metrics."""
    sections = []
    for name in assign.load_tests():
        rows = "".join(
            _DASH_ROW.format(
                variant=escape(str(r["variant"])),
                impressions=r["impressions"],
                actions=escape(", ".join(f"{k}={v}" for k, v in r["actions"].items()) or "-"),
                rate=r["conversion_rate"],
            )
            for r in store.summarize(name)
        )
        sections.append(
            f"<h2>{escape(name)}</h2><table border=1 cellpadding=6>"
            f"<tr><th>variant</th><th>impressions</th><th>actions</th>"
            f"<th>conv. rate</th></tr>{rows or '<tr><td colspan=4>no data yet</td></tr>'}</table>"
        )
    return (
        "<title>Analytics service</title>"
        "<h1>Analytics service</h1>"
        "<p>A/B assignment + event store. Endpoints: "
        "<code>/healthz</code> <code>/variant</code> <code>/variants</code> "
        "<code>/events</code> <code>/metrics/&lt;test&gt;</code></p>"
        + "".join(sections)
    )


@app.get("/healthz")
def healthz():
    return jsonify(status="ok")


@app.get("/variant")
def variant():
    test = request.args.get("test", "")
    visitor = request.args.get("visitor", "")
    return jsonify(test=test, variant=assign.variant_for(test, visitor))


@app.get("/variants")
def variants():
    return jsonify(assign.all_variants(request.args.get("visitor", "")))


@app.post("/events")
def events():
    data = request.get_json(silent=True) or {}
    test = data.get("test")
    event = data.get("event")
    if not event or not test:
        return jsonify(error="'event' and 'test' are required"), 400

    variant_value = data.get("variant")
    if variant_value is None:
        variant_value = assign.variant_for(test, data.get("visitor"))

    store.write_ab_log({
        "event": event,
        "test": test,
        "variant": variant_value,
        "visitor": data.get("visitor"),
        "timestamp": data.get("timestamp") or datetime.now().isoformat(),
    })
    return jsonify(status="recorded"), 202


@app.get("/metrics/<test>")
def metrics(test):
    return jsonify(test=test, summary=store.summarize(test))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
