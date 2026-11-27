---
name: rotation-relativity-ratios
description: Computes 1:x price ratios and relationship weights between a stock and NVDA, MSFT, SMH and QQQ, with ratio z-scores, percentiles, half-life and zone traversals. Use when asked how a name trades relative to references, for profiles/<T>.json, ratio history, or repeated price-zone crossings.
compatibility: Python 3 stdlib; CLI cli profile, cli report.
metadata:
  owner: B04
  version: 1.0.0
---
# Relativity ratios

Detail: `../prompts/RELATIVE_ROTATION_PROFILE_PROMPT.md` sections 3-4.

## Formulas
`x = P_subject / P_reference` for each reference; `d ln x = r_subject - r_reference`. Weights from R2 of regressing the subject on each reference, normalised; z-score and percentile over 250 days; AR(1) half-life of ln x. Zones: 4% log bins, dwell days, visits, volume share, level crossings.

## Procedure
1. Require `history/<T>.jsonl` for subject and references on one date grid; stop if missing.
2. Report valuation track and trading track separately, then reconcile (is the ratio move price, EPS or multiple).
3. Compare trailing to trailing only; never trailing history against forward multiples (this produced a false +190% on NVDA).

## Stop rules
Ratios from different adjustment bases are invalid. A ratio extreme is a lead, not a signal.

## Hands off to
`rotation-group-sympathy`, `rotation-swap-decision`.
