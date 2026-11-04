# ETF forward valuation — B04 offline component (experimental)

Engine version: `etf-forward@0.1.0`. Output contract: `basket.etf_forward_output@1` (module-local candidate, not approved shared schema). This is **not** a live ETF ranking or issuer reconciliation.

Run: `cd engines/valuation/etf_forward && python -m unittest -v test_engine.py`

CLI: `python engine.py input.json --output result.json`. Import `analyze(data)` and `sensitivity(yield, earnings_revisions, multiple_factors)`.

Inputs require timestamped holdings and calendarized USD net-income estimates available no later than `as_of`; weights must sum to 1 including cash. Estimates after as-of are rejected. Positive, complete aggregated earnings yield yields reciprocal P/E; negative aggregate earnings or partial coverage suppresses P/E. Sensitivity decomposes conditional price change into earnings, multiple and interaction terms. Canonical sorted input JSON hashes for repeatability.

**Limitations / blocked acceptance**: no entitlement-backed holdings ingestion, issuer holdings snapshots, share-class/ADR FX conversions, fiscal calendarization, historical point-in-time revisions, real issuer FY2027/2028 consensus, fund-owned-share reconciliation, fees/tracking, forward growth, historical SMH October 30 attribution or actual stress-risk calibration. These MUST NOT be assumed from this prototype. Foreign reporting and non-USD inputs fail closed. No actual ETF or constituent return, earnings multiple, or opportunity claim is supported.

Next: request B02/B03 source-adapter interface and B01 exact-head execution; B00 approval for any cross-domain schema. No other spark's files may be changed.

## Incremental maturation — dual-horizon economic look-through

`lookthrough.py` provides `calculate(snapshot)` with a separate module-local candidate output `basket.etf_lookthrough@1`. It does **not** replace the legacy `engine.analyze` contract; downstream adapters must choose the correct version explicitly until B00 approves schema evolution. Only `equity` and explicitly USD `cash` are supported; derivative/negative-asset positions fail closed. The cash assumption is **zero earnings yield**, not a claim about the actual fund's interest income. Loss-making equity earnings remain signed. Full equity estimate coverage and positive aggregate fund yield are required before emitting P/E. Individual-year coverage and P/E validity are distinct.

Minimal input:
```json
{
  "as_of":"2026-10-30T20:00:00Z",
  "data_kind":"synthetic_test",
  "source_manifest":[{"id":"toy-only"}],
  "holdings_available_at":"2026-10-29T20:00:00Z",
  "holdings":[
    {"id":"EXAMPLE","asset_type":"equity","available_at":"2026-10-29T20:00:00Z","weight":"0.9","equity_currency":"USD","market_cap_usd":"100","estimates":{
      "2027":{"calendar_year":2027,"available_at":"2026-10-29T20:00:00Z","currency":"USD","net_income_usd":"10"},
      "2028":{"calendar_year":2028,"available_at":"2026-10-29T20:00:00Z","currency":"USD","net_income_usd":"15"}
    }},
    {"id":"CASH","asset_type":"cash","available_at":"2026-10-29T20:00:00Z","currency":"USD","weight":"0.1"}
  ]
}
```

To run **all** B04 domain unit tests:
```bash
cd engines/valuation/etf_forward
python -m unittest discover -p 'test_*.py' -v
```

The source manifest is passed through and hashed, **not cryptographically verified** against issuer documents. An upstream approved adapter must establish issuer provenance, original currency/FX pair/date, share classes/ADR ratio, available/ingested times and TTD. Therefore `verified_observation` is a **caller assertion**, not independent proof. Direct fund ownership/share-unit reconciliation, derivatives, expenses, dividends, dynamic rebalancing, risk-adjusted winner selection and real 2027/2028 consensus integration remain open. New local `test_lookthrough.py` checks 11 negative/correctness cases; local success is **not** SHA-matched independent GitHub CI.
