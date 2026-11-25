# Time to Die (TTD) — local-first execution contract

TTD is **Time to Die**, not Time to Data. Observations and computations have short, explicit valid lifetimes. After expiration the last observation remains in append-only JSONL for replay, but cannot be presented as live or used for current NAV without explicit stale/provisional handling.

`runtime/feeds.json` declares predetermined feed paths, intervals, expiry policies and dependencies. `runtime/ttd.py` implements ingestion, append-only persistence, status and optional local adapter polling. All feeds start **disabled** until a real, entitled data adapter is configured. GitHub stores source code; it is **not** a continuously running local ingestion host.

Example:
```sh
python runtime/ttd.py status
python -m unittest discover -s tests -p 'test_ttd.py'
```

## Where the current 1-minute data lives (checked 2026-11-25 by reading code; not run, not independently verified)
Components that need minute bars must read them from the local data plane, **not from this repository**.
- **Location:** one file per ticker per America/New_York session date, `_TICKERS/<T>/snapshots/<YYYY-MM-DD>.jsonl`, in the **private** repository `whiterosecoffee/_PATTERNS` (main) and in the owner's local checkout of it (the `ROOT` constant in `_PATTERNS/_TOOLS/ticker_rows.py` names the local directory; it is deliberately not repeated here). Example: `XLE` had 555 day files, 2024-09-09 to 2026-11-23, when read.
- **Content:** 1-minute **bars** (aggregates, not trade ticks), unadjusted, one JSON object per line with named fields `ticker, t (ms, bar start), ts, px, vol, o, h, l, c, vw, n, src, class, grain` and an optional `verified` flag. A file whose rows are all `verified` is frozen.
- **Writer:** `_PATTERNS/_TOOLS/ticker_tail.py` through `ticker_rows.add_rows` (dedupes on `t`, appends under a lock, never rewrites a line, skips frozen days). The writer reads the API key from a local file outside any repository (path in `ticker_tail.py`); never put a key in this repository.
- **Not here:** `tickers/<T>/history.jsonl` in this repository is the daily-bar store (AAOI, CRWV, SFTBY). `tickers/*/intraday/` holds only one SFTBY 5-minute file. No 1-minute store is committed here.
- **Status:** the 2026-10-09 to 2026-11-23 backfill rows were reported unverified by their writer; completeness and quality are unestablished. A B00 ruling (issue #207, R1) names a different target path, `<root>/tickers/<T>/intraday/<YYYY-MM-DD>.1m.jsonl`; the mapping between the two is unresolved (#148). Do not assume either is current for your use without checking the owner.
- Details and open gaps: `runtime/fetch/ARCHITECTURE.md` and `runtime/fetch/massive/API_NOTES.md`.

Feed adapters output one JSON object containing `entity_id`, `observed_at` (timezone-aware UTC recommended), `source`, and `value`. Do not embed API keys in the repository. `run` executes a trusted local command repeatedly; it does not magically create a live feed. For reliability, supervise it with Windows Task Scheduler, systemd, or an always-on worker, with durable writable storage and a single writer per feed.

## Pending production hardening
- Durable queue and multi-process-safe locking on all operating systems.
- Corporate action and vendor revision reconciliation.
- Trading calendars, exchange closures, provider delays, and explicit no-trade intervals.
- Live provider entitlement, timestamp accuracy and automatic reconnect/backoff.
- Cross-feed event triggers and dependency graph recomputation.
- Observability, latency alerts, snapshot atomicity, tests against real source adapters.
