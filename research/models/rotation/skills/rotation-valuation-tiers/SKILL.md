---
name: rotation-valuation-tiers
description: Builds per-stock valuation models - calendarised EPS, forward multiples 2026-2030, P/E at max compression and peak rebound, and price-band tiers that migrate after EPS updates. Use when asked for fair value, multiples at two points, tier or band spreads, EPS-update effects, or models/<T>.json.
compatibility: Python 3 stdlib; CLI cli models, cli multiples, cli anchors.
metadata:
  owner: B04
  version: 1.0.0
---
# Valuation and tiers

Detail: `references/tier-math.md` and `../prompts/MASTER_MODEL_PROMPT.md` section 3.

## Procedure
1. Choose E: TTM EPS, or TTM sales per share when EPS <= 0. Multiple `M = price / E`.
2. Tier bounds in multiple space: five tiers equal in log space between M at the 52-week low and M at the 52-week high; below is tier 0, above tier 6.
3. Bands `= E x bounds`. After an EPS update `E -> E'`, bands shift by `E'/E - 1` and the bounds do not; an unchanged price changes tier.
4. Label the mode every time: `point_in_time` (NVDA, SNDK, CRWV) or `constant_current_E_counterfactual` (all others).
5. Record P/E at the stress low and at the rebound peak with EPS held fixed; when EPS changed between points, label the move mixed.
6. Forward view: calendarise fiscal years, fade growth (x0.8, capped -20%..+50%), reverse-DCF implied growth at 10y yield + 4.5% ERP, terminal g 3%.

## Stop rules
Missing EPS: stop that calculation and list the gap. A tier is a position in the stock's own range, not cheapness. Hypothetical EPS grids are scenarios.

## Hands off to
`rotation-swap-decision`, `rotation-audit-qa`.
