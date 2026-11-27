---
name: rotation-stress-rebound
description: Ranks tickers by distance above the 52-week low and drawdown from the 52-week peak, and measures how often such states were followed by positive or market-beating returns, from the daily ticker store. Use when asked which names are closest to their lows or furthest off their peaks, what the odds of a rebound have been, or how a stress day compares across the basket.
compatibility: Python 3 stdlib; reads _PATTERNS _TICKERS/<T>/snapshots read-only; CLI cli rebound.
metadata:
  owner: B04
  version: 1.0.0
---
# Stress and rebound

Code: `engines/valuation/relative_value/rebound.py` and `snapshots.py`. Output schema `rotation.rebound/1`.

## Procedure
1. Point `--snapshots` at the store (`_PATTERNS/_TICKERS`). Run `python -m engines.valuation.relative_value.cli rebound --snapshots <root> --out <file> --as-of-floor <date>`.
2. Read the ranking: `dist_low = close/52w low - 1`, `dd = close/52w high - 1`, score = mean percentile of closeness to the low and depth of drawdown.
3. Check `split_suspect` before using any name: unadjusted prices make splits look like crashes (SNDK, ITA, KYCCF, IBIDY in the first run). Confirm each against filings, never assume.
4. Read the study as frequencies: `p_up`, `p_beat_median_stock` (versus the same-date median) with a 90% interval that resamples whole dates. State the window (about 14 months) and that it is one regime.

## What the first run found (2026-11-24, 328 names, before the split guard; figures to be regenerated)
Being near the low alone gave no edge (about 51% up, 47-49% beating the median stock); a drawdown of 60% or more did worse (median 20-day return -2.5%); near the low with a 40%+ drawdown was modestly positive (about 53% beating the median, 80 tickers). Treat as hypotheses to test out of sample.

## Stop rules
No ranking from stale, short or split-suspect names. Price-only days understate extremes: report `price_only_share`. Not a forecast or a trade instruction.

## Hands off to
`rotation-group-sympathy` (was the move shared), `rotation-swap-decision` (use only after the audit passes), `rotation-audit-qa`.
