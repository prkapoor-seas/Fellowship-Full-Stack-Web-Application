# Analytics service

One of the two backend services. Owns the A/B test registry (`ab_tests.json`)
and the event store (`ab_events.sqlite`). The main application talks to it only
over HTTP (see `../analytics_client.py`).

## Run locally

```bash
# from the repo root
python -m analytics.app                 # dev server on :8000
# or
gunicorn -w 1 -b 0.0.0.0:8000 analytics.app:app
```

`-w 1`: SQLite has a single writer. WAL mode still lets metrics reads run
concurrently.

## API

| Method | Path | Purpose |
| ------ | ---- | ------- |
| GET  | `/healthz` | Liveness / readiness probe |
| GET  | `/variant?test=<name>&visitor=<id>` | Variant for one test |
| GET  | `/variants?visitor=<id>` | `{test: variant}` for every test |
| POST | `/events` | Record an event `{event, test, visitor, variant?, timestamp?}` |
| GET  | `/metrics/<test>` | Per-variant impressions / actions / conversion rate |

Variant assignment is stateless: `sha256(visitor_id:test) % len(variants)`.
Same visitor + test always maps to the same variant, no storage required.

## Config

| Env var | Default | Meaning |
| ------- | ------- | ------- |
| `PORT` | `8000` | Port for the dev server (`__main__` only) |
| `AB_DB_PATH` | `./ab_events.sqlite` | SQLite file location (point at a volume in a container) |
