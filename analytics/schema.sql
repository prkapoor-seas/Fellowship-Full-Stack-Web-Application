-- Schema for the Analytics service event store (ab_events.sqlite).
--
-- Owned solely by the Analytics service; the main application never touches it.
-- Created automatically on first write by store.py; kept here for reference and
-- manual setup.

PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS ab_events (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    event      TEXT NOT NULL,   -- 'variation_presented', or a target-action name
    test       TEXT NOT NULL,   -- test name, matches a key in ab_tests.json
    variant    TEXT,            -- variant the visitor was shown (may be NULL)
    visitor    TEXT,            -- opaque visitor id sent by the main app
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_ab_events_test_variant ON ab_events (test, variant);
CREATE INDEX IF NOT EXISTS idx_ab_events_test_event   ON ab_events (test, event);
