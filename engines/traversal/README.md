# B06 canonical traversal metrics (incremental takeover)

Read-only metrics extension to main's `engines/traversal/range.py`. It computes descriptive observed extrema for simultaneous 5/15/60/390-minute horizons. Import `from engines.traversal.metrics import evaluate`, or run:

```sh
python engines/traversal/run_metrics.py CRWV --jsonl /path/to/completed-minute-bars.jsonl --interval 1 --as-of-ms 1793280000000
python -m unittest discover -s engines/traversal/tests -v
```

Records must be completed ordered bars containing `t` (UTC start milliseconds), `o,h,l,c,v` and optional `vw`. An older 8-element array format is also accepted. Each horizon demands complete contiguous bars; gaps/missing samples produce null. A session-aware caller must filter sessions; exchange calendars and early closes are **not implemented** by this module. No fabricated bars.

## Contract and scope
- Method `basket.traversal.metrics@1`; observed range position does not imply direction. Velocity in USD/min is based on the *fixed window*, not a changing boundary. Normalized band velocity remains null until frozen reference versions are available.
- Turnover is shares times supplied VWAP, otherwise typical-price approximation; directional movement per USD uses candle-to-candle positive/negative close changes and associated next-bar turnover. This is **not signed trade volume**. Efficiency ratio requires three up and three down movements; otherwise null. ADV and same-clock RVOL require caller-supplied actual baselines, never invented.
- Deliberately returns null for frozen-band events, contact episodes, structural regime, market context and estimated acceleration. Their authoritative producer is B10 PR #99; context is B17 PR #101. Do not confuse these with observed extrema.
- Caller is responsible for source provider, entitlement, available_at and TTD; source_quality is explicitly *not_attested* and no alerts are enabled. No SQLite or hosted storage is created.

## Existing components retained
- `engines/traversal/range.py`: legacy daily static range reader, unchanged.
- PR #99: B10 completed-bar producer, SQLite append-only journal/revision checkpoint, contact/break events, historical matcher and poller; **not copied**.
- PR #101: market-context computation, separate adapter contract; **not copied**.

## Next dependent integration
B00 #96 must register the final capability. B06 must review and adapt PR #99 event/output schema after merge or explicitly pinned dependency; B02/B08 #97 must prove durable provider execution; B01 #98 must perform independent exact-head acceptance. ORCL source coverage and the external `_DATA` archive are not verified by this module. Production/readiness claims remain blocked. No live watch reactivation.
