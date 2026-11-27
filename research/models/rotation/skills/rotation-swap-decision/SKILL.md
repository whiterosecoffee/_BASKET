---
name: rotation-swap-decision
description: Evaluates a spot rotation from stock A to stock B using share-count identity, expected end value, triggers, weights and friction, as a virtual ETF with adjusting weights. Use when asked whether swapping one name for another improves share count or expected end value, or to rebalance weights toward better growth per spot price. No holdings or cost basis are required.
compatibility: Python 3 stdlib; CLI cli swap, cli rebalance, cli simulate.
metadata:
  owner: B04
  version: 1.0.0
---
# Swap decision

## Formulas
`shares_B = shares_A x P_A / P_B`; end-value ratio `= (1 + r_B) / (1 + r_A)`; weights proportional to mu/sigma with a cap; no-trade band; staged entries into new lows; tax and cost friction as inputs, not assumptions.

## Procedure
1. Take target prices from the three anchors: F standardised estimates, I industry forecasts (explicit assumption mapping), R ratio reversion (low weight); blend 50/30/20.
2. Flag ANCHOR_DISAGREE when anchors diverge (halves the weight cap). Band = realised vol clamped 15-50%.
3. Report scenarios (base, bear, bull) and the break-even ratio; state which inputs are assumptions.

## Stop rules
Output is a scenario, never an instruction to trade, no personalised advice. Do not use if valuation or ratio inputs failed their gates.

## Hands off to
`rotation-audit-qa`.
