# CRWV minute history

Canonical data path proposed in PR122: `tickers/CRWV/intraday/2026-10.1m.jsonl`.
Existing `tickers/CRWV/history.jsonl` remains **daily**, unchanged. Do not mix intervals.

19,186 observed one-minute OHLCV bars, October 1 through October 30, 2026
12:10 ET; 22 session dates. This is a dated backfill, not a continuously running feed.
Minute aggregates are **not individual trade ticks**. All returned premarket,
regular-session and after-hours observations are retained. The latest day is partial.

Each JSONL line follows the existing repository `market.intraday@1` array layout:

`[timestamp_ms, open, high, low, close, volume, vwap, transactions]`

Timestamps mark UTC minute starts. Interpret session dates in America/New_York.
Read `2026-10.1m.meta.json` for hash, source requests, per-month counts and quality limits.
No bars are interpolated. Daily aggregates and minute regular-session sums are
not interchangeable; closing auctions, sale-condition eligibility, extended hours
and source revisions can affect reconciliation. VWAP values outside the reported
minute OHLC are retained as returned and flagged in validation; do not regard
turnover estimates as exchange-certified signed flow.

Validation/replay from the repository root, given the original Massive MCP CSV
transport captures in an external directory:

```bash
python research/CRWV/market-research-2026-10-29/backfill_minutes.py --source-dir /path/to/captures --root .
```

Replay of identical captures adds zero records. Conflicting observations fail
closed. Existing-record revisions and older missing intervals require an audited
backfill/revision generation rather than silent overwrites. No credentials needed
for this offline check. The original CSV transport files are not duplicated here;
the JSONL preserves all eight price/volume/count fields and metadata hashes them.

Recent analysis: `research/CRWV/market-research-2026-10-29/recent-history-2026-10-30.json`.
Discovery/integration remains with B00/B02/B06. No merge or live-service claim.
