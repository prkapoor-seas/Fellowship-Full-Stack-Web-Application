"""
ab_test_log.py

Event store for A/B testing, backed by a dedicated SQLite database
(ab_events.sqlite), kept separate from labsatyale.sqlite.

Why SQLite instead of a JSON file:
    - each event is a single INSERT, not a full-file rewrite, so the
      load-generating simulation scripts can emit thousands of events cheaply;
    - WAL mode lets readers (metrics queries) run without blocking the writer;
    - per-variant metrics are one GROUP BY query instead of loading everything
      into Python.

Public interface:
    write_ab_log(data)      -- append one event; `data` is the dict that
                               ab_testing.py already builds
                               ({event, test, variant, timestamp}).
    summarize(test_name)    -- per-variant impression / action / conversion-rate
                               summary for a test.
"""

from contextlib import closing
from datetime import datetime
from sqlite3 import connect
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "ab_events.sqlite")
_SCHEMA_FILE = os.path.join(os.path.dirname(__file__), "ab_events_schema.sql")

_initialized = False


def _init_db():
    """Create the ab_events table (and enable WAL) once per process."""
    global _initialized
    if _initialized:
        return
    with open(_SCHEMA_FILE, "r") as f:
        schema = f.read()
    with closing(connect(DB_FILE)) as conn:
        conn.executescript(schema)
        conn.commit()
    _initialized = True


def write_ab_log(data):
    """
    Append one event to the store.

    `data` is expected to contain 'event', 'test', 'variant', and 'timestamp'
    (the shape ab_testing.py produces). Missing keys are tolerated: the
    timestamp falls back to now, other fields to NULL.
    """
    _init_db()
    # timeout + busy_timeout: under concurrent load (e.g. the simulation
    # scripts) writers wait for the lock instead of raising "database is locked".
    with closing(connect(DB_FILE, timeout=10.0)) as conn:
        conn.execute("PRAGMA busy_timeout = 10000")
        conn.execute(
            """
            INSERT INTO ab_events (event, test, variant, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                data.get("event"),
                data.get("test"),
                data.get("variant"),
                data.get("timestamp") or datetime.now().isoformat(),
            ),
        )
        conn.commit()


def summarize(test_name):
    """
    Return a per-variant summary for `test_name`:

        [
            {
                "variant": "A",
                "impressions": 120,          # 'variation_presented' events
                "actions": {"student_signup_click": 30, ...},
                "conversion_rate": 0.35,     # total actions / impressions
            },
            ...
        ]

    Sorted by variant name. Variants with no impressions get a rate of 0.0.
    """
    _init_db()
    with closing(connect(DB_FILE)) as conn:
        rows = conn.execute(
            """
            SELECT variant, event, COUNT(*)
            FROM ab_events
            WHERE test = ?
            GROUP BY variant, event
            ORDER BY variant, event
            """,
            (test_name,),
        ).fetchall()

    variants = {}
    for variant, event, count in rows:
        entry = variants.setdefault(
            variant, {"variant": variant, "impressions": 0, "actions": {}}
        )
        if event == "variation_presented":
            entry["impressions"] += count
        else:
            entry["actions"][event] = entry["actions"].get(event, 0) + count

    for entry in variants.values():
        total_actions = sum(entry["actions"].values())
        entry["conversion_rate"] = (
            round(total_actions / entry["impressions"], 4)
            if entry["impressions"]
            else 0.0
        )

    return sorted(variants.values(), key=lambda e: (e["variant"] is None, e["variant"]))
