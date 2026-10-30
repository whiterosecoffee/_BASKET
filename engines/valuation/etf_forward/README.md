# ETF forward valuation — B04 offline component (experimental)

Engine version: `etf-forward@0.1.0`. Output contract: `basket.etf_forward_output@1` (module-local candidate, not approved shared schema). This is **not** a live ETF ranking or issuer reconciliation.

Run: `cd engines/valuation/etf_forward && python -m unittest -v test_engine.py`

CLI: `python engine.py input.json --output result.json`. Import `analyze(data)` and `sensitivity(yield, earnings_revisions, multiple_factors)`.

Inputs require timestamped holdings and calendarized USD net-income estimates available no later than `as_of`; weights must sum to 1 including cash. Estimates after as-of are rejected. Positive, complete aggregated earnings yield yields reciprocal P/E; negative aggregate earnings or partial coverage suppresses P/E. Sensitivity decomposes conditional price change into earnings, multiple and interaction terms. Canonical sorted input JSON hashes for repeatability.

**Limitations / blocked acceptance**: no entitlement-backed holdings ingestion, issuer holdings snapshots, share-class/ADR FX conversions, fiscal calendarization, historical point-in-time revisions, real issuer FY2027/2028 consensus, fund-owned-share reconciliation, fees/tracking, forward growth, historical SMH October 30 attribution or actual stress-risk calibration. These MUST NOT be assumed from this prototype. Foreign reporting and non-USD inputs fail closed. No actual ETF or constituent return, earnings multiple, or opportunity claim is supported.

Next: request B02/B03 source-adapter interface and B01 exact-head execution; B00 approval for any cross-domain schema. No other spark's files may be changed.
