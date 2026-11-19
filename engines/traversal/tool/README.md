# B06 traversal readout tool (experimental)

This is a **thin read-only adapter** to the already merged `engines/traversal/metrics.py`. It does not create another engine, store, poller, delivery cursor, alert rule, or market feed. Historical output is descriptive. **Current mode always fails closed** until a B00/B02-approved source resolver provides independently verifiable data and entitlement evidence. A self-reported JSON value of `realtime` does not qualify a source.

## Invoke

```sh
python -m engines.traversal.tool.run --input /path/to/request.json --mode historical
python -m unittest engines.traversal.tool.test_tool -v
```

Input request `basket.traversal.request@1` is a JSON object with `instrument` (CRWV or ORCL, or any valid instrument), `as_of_ms` (UTC milliseconds), `observations` (ordered completed OHLCV dictionary or legacy eight-field arrays), and `source`. Required source fields: `provider`, `source_id`, `interval_minutes` (1,5,15), `currency` (USD), `adjustment_basis`, `session`, and `sha256` (SHA256 of compact sorted-key JSON of the observation array). Optional/asserted metadata: `available_at_ms`, `received_at_ms`, `ttd_ms`, `quality`, `completeness`, `calendar_verified`, `entitlement`.

A matching digest proves **request-content integrity only**, not vendor provenance, exchange completion, licensing, or successful source retrieval. Numeric timestamps refer to UTC bar START times. The last completed bar must end no later than `as_of_ms`. Gaps, unknown freshness, unverified entitlement and calendars are explicitly reported. No bars are filled. No data is persisted.

Output `basket.traversal.tool@1` contains `status`, `reasons`, `completed_at_ms`, `as_of_ms`, `observation_sha256`, the existing core `metrics` for historical runs, and `alerts_emitted=0`. A current-mode request returns `blocked_current`, `metrics=null`, and CLI exit code 2.

## Boundaries and next gate

- Existing #108/merged #109 owns the metric computation; B10 #95/PR99 owns the local event producer/journal, B17 #100 owns market-context work.
- B00 #148 must resolve approved authoritative `_TICKERS/{instrument}` inputs and source-quality/availability semantics; do not silently bypass to legacy history or copy JSONL into this folder.
- B01 #98 must independently validate this exact PR source; the local synthetic tests do not establish operational replay or a live source.
- B00 #96 must register the final entrypoint; this local manifest is **not a shared registry entry**.
- #108 CRWV+ORCL source → frozen range → event journal → readable output is still open, as are calendar/no-trade, correction, restart and delivery gates. **No watch reactivation.**
