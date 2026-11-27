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
Out: `ratios.csv`, `estimates.csv`, `guidance.csv`, `events.csv`, `multiple_events.csv`, `fundamentals/*`. Price history is NOT stored here: the source of truth is the `_PATTERNS` snapshot store (below). `prices/*.csv` and `history/*.jsonl` (6 names) are legacy fixtures from the first build; prefer the store.

## Procedure
1. State vendor, adjustment basis and snapshot time before storing anything.
2. Fetch, then verify against an independent figure (a checksum such as a grouped-daily sum, or a typed-in price cross-check). Differences above 0.5% mean use the vendor value and flag the other.
3. Normalise: split-adjust share counts to one basis (SNDK 8-for-1 effective 2026-11-20 mixed bases in Massive); if filing_date is missing or more than a year after period end, use period_end + 45 days and mark it `derived`.
4. Mark any value from an open session `provisional` (file name carries the time; never overwrite a final file).
5. Regenerate history: `python -m engines.valuation.relative_value.cli history-export`.
6. Record every estimate or guidance row with `kind` (actual, consensus, house, guidance), source URL and as-of date.

## Stop rules
- Unverified bars, mixed adjustment bases or an unknown split state: stop, list the gap.
- Never impute a missing bar or EPS. Estimates older than 120 days are not used for current claims.
- Do not write under `_TICKERS/` (another spark owns it); read manifests by snapshot copy only.

## Price source of truth (as of 2026-11-24)
`_PATTERNS` `_TICKERS/<T>/snapshots/<YYYY-MM-DD>.jsonl`: 356 symbols, 1-minute rows, one New York date per file, 2024-09-09 to 2026-11-23, on `main` (commit 459f8806 and later). Rule set: `_PATTERNS/AGENTS.md` "Authoritative ticker data" (check local snapshots first; fetch only gaps through the `_MASSIVE-API` tool; one write path `ticker_rows.add_rows`). This toolkit reads the store through `engines/valuation/relative_value/snapshots.py` and never writes to it.
Row: `ticker, t, ts, px, vol, o, h, l, c, vw, n, src, class, grain [, verified]`. `class: bar` has real OHLC; `class: moment` is price-only (o, h, l, c, vw, n null; px is the minute close). Facts measured on 2026-11-24: 51.8M bar rows and 26.7M moment rows; moments cover 233 tickers for 2025-09-10 to 2026-09-11. Only 3,670 rows (AAPL 2025-01-02..08 pilot) are `verified: true`; bulk verification is deferred by the store's owner. Index and FX folders (`I_*`, `C_*`) carry volume 0; YAGOY has no bars.
Prices are as stored, not split-adjusted: SNDK 8-for-1 (2026-11-20) and several others show as one-day crashes; `rebound.py` flags and excludes them (`split_suspect`).

## Gaps to state
Price-only minutes understate daily highs and lows; unverified rows are vendor values as fetched on their fetch date (VWAP restatement was measured at 12% of overlapping bars in October). 20 tradable names have no Massive bars; the universe is 297 identifiers against an expected 300+. Estimates come from Yahoo consensus (secondary), company guidance and filings; Massive's Benzinga and Quartr feeds are not entitled.

## Hands off to
`rotation-universe-hierarchy` (symbols and groups), `rotation-valuation-tiers` (E and M inputs), `rotation-audit-qa` (checks).
