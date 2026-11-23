---
name: rotation-data-steward
description: Ingests and normalises market and fundamental data for the rotation toolkit (Massive bars, splits, TTM EPS, filings) and writes per-ticker history JSONL with provenance. Use when adding or refreshing prices, ratios, estimates, guidance or fundamentals, when a split or provisional intraday session is involved, or when history/<T>.jsonl is missing.
compatibility: Python 3 stdlib; Massive MCP (call_api, query_data). Benzinga estimates and Quartr are not entitled, so consensus is secondary-sourced and labelled.
metadata:
  owner: B04
  version: 1.0.0
---
# Data steward

## Inputs and outputs
In: Massive grouped-daily and per-ticker aggregates, `/stocks/financials/v1/ratios`, income statements, filings, press releases.
Out: `prices/<T>.csv`, `history/<T>.jsonl` (fields `t, date, open, high, low, close, volume`; benchmarks carry `close` only), `ratios.csv`, `estimates.csv`, `guidance.csv`, `fundamentals/*`, `prices/SOURCE.json`.

## Procedure
1. State vendor, adjustment basis and snapshot time before storing anything.
2. Fetch, then verify against an independent figure (a checksum such as a grouped-daily sum, or a typed-in price cross-check). Differences above 0.5% mean use the vendor value and flag the other.
3. Normalise: split-adjust share counts to one basis (SNDK 8-for-1 effective 2026-11-20 mixed bases in Massive); if filing_date is missing or more than a year after period end, use period_end + 45 days and mark it `derived`.
4. Mark any value from an open session `provisional` (file name carries the time; never overwrite a final file).
5. Regenerate history: `python -m engines.valuation.rotation.cli history-export`.
6. Record every estimate or guidance row with `kind` (actual, consensus, house, guidance), source URL and as-of date.

## Stop rules
- Unverified bars, mixed adjustment bases or an unknown split state: stop, list the gap.
- Never impute a missing bar or EPS. Estimates older than 120 days are not used for current claims.
- Do not write under `_TICKERS/` (another spark owns it); read manifests by snapshot copy only.

## Gaps to state
Only NVDA, CRWV, SNDK, MSFT, SMH and QQQ have full history files; about 240 basket names still need one per-ticker fetch each. 20 tradable names (mostly OTC ADRs) have no Massive bars; indices, futures and FX need their own feed.

## Hands off to
`rotation-universe-hierarchy` (symbols and groups), `rotation-valuation-tiers` (E and M inputs), `rotation-audit-qa` (checks).
