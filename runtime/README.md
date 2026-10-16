# Time to Die (TTD) — local-first execution contract

TTD is **Time to Die**, not Time to Data. Observations and computations have short, explicit valid lifetimes. After expiration the last observation remains in append-only JSONL for replay, but cannot be presented as live or used for current NAV without explicit stale/provisional handling.

`runtime/feeds.json` declares predetermined feed paths, intervals, expiry policies and dependencies. `runtime/ttd.py` implements ingestion, append-only persistence, status and optional local adapter polling. All feeds start **disabled** until a real, entitled data adapter is configured. GitHub stores source code; it is **not** a continuously running local ingestion host.

Example:
```sh
python runtime/ttd.py status
python -m unittest discover -s tests -p 'test_ttd.py'
```

Feed adapters output one JSON object containing `entity_id`, `observed_at` (timezone-aware UTC recommended), `source`, and `value`. Do not embed API keys in the repository. `run` executes a trusted local command repeatedly; it does not magically create a live feed. For reliability, supervise it with Windows Task Scheduler, systemd, or an always-on worker, with durable writable storage and a single writer per feed.

## Pending production hardening
- Durable queue and multi-process-safe locking on all operating systems.
- Corporate action and vendor revision reconciliation.
- Trading calendars, exchange closures, provider delays, and explicit no-trade intervals.
- Live provider entitlement, timestamp accuracy and automatic reconnect/backoff.
- Cross-feed event triggers and dependency graph recomputation.
- Observability, latency alerts, snapshot atomicity, tests against real source adapters.
