---
name: rotation-two-point-compare
description: Compares a price at point A with point B (for example Friday close versus Monday high) across tickers, references and groups, under the validity gate V1-V8. Use when asked how far a stock moved between two named moments, how much of a drop was recovered, or to produce comparisons/<A>__vs__<B>.json.
compatibility: Python 3 stdlib; CLI engines.valuation.rotation.cli compare
metadata:
  owner: B04
  version: 1.0.0
---
# Two-point comparison

Contract: `../AGENTS.md` (validity gate V1-V8, required metrics, output schema `rotation.compare/1`). Read it first; this skill is the short procedure.

## Procedure
1. Fix pair (A, B) and snapshot time; points come from the registry in `pointcompare.POINTS`.
2. Run the gate: same adjustment and share basis, provisional points labelled, A not later than B (path comparisons labelled), missing points excluded not imputed.
3. `python -m engines.valuation.rotation.cli compare --a fri_close --b mon_high`.
4. Report subjects first (NVDA, CRWV, SNDK), then cohort and peer-group medians, flags, limits.

## Formulas
`change = B/A - 1`; recovery of drop `= (B - fri_close)/(thu_close - fri_close)`; giveback `= last/B - 1`; a peak is always paired with the A-to-last change.

## Stop rules
A failed gate means report INVALID with the reason, no numbers. No annualising, no targets, no advice.

## Hands off to
`rotation-valuation-tiers` (multiples at A and B), `rotation-group-sympathy` (is the move shared).
