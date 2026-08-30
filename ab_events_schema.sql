-- Schema for the A/B testing event store (ab_events.sqlite).
--
-- This database is separate from labsatyale.sqlite so that analytics writes --
-- including the high-rate load from the simulation scripts -- never contend
-- with the main application database, and so it can be wiped and regenerated
-- freely between experiment runs.
--
-- It is created automatically on first write by ab_test_log.py; this file is
-- kept for reference and manual setup.

PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS ab_events (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    event      TEXT NOT NULL,   -- 'variation_presented', or a target-action name
    test       TEXT NOT NULL,   -- test name, matches a key in ab_tests.json
    variant    TEXT,            -- variant shown to the visitor (may be NULL)
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_ab_events_test_variant ON ab_events (test, variant);
CREATE INDEX IF NOT EXISTS idx_ab_events_test_event   ON ab_events (test, event);
