---
name: rotation-group-sympathy
description: Measures sympathetic response and relative movement inside nested groups (market, sector, peer group, name) - intraclass correlation, sequential betas, up/down asymmetry, lead-lag, idiosyncratic residuals. Use when asked whether a move was shared by a peer group, who leads, which names diverged, or how a group-relative ratio should be built.
compatibility: Python 3 stdlib; engines.valuation.relative_value.sympathy; basket output key sympathy_peer_groups.
metadata:
  owner: B04
  version: 1.0.0
---
# Group sympathy

Formulas and prior art: `../prompts/AUDIT_AND_DECOMPOSITION.md` sections 4-5 and `references/formulas.md`.

## Procedure
1. Take returns ex-self: group mean excludes the name being scored.
2. One event (cross-section): report ICC(1), slope on the ex-self group mean, per-name residual. Never regress on a leave-one-out cohort mean (slope forced toward -(n-1)).
3. With history: sequential betas market > sector > peer group, down-beta versus up-beta, lead-lag k = 0..5, shrinkage for groups under 10 names.
4. In stress sessions adjust correlation with the Forbes-Rigobon factor before calling a rise contagion.

## Latest measurement
43 equities in 8 peer groups: ICC(1) 0.29 (Friday flush), 0.15 (Monday rebound, provisional). The rebound was mostly name-specific.

## Stop rules
Groups under 3 names: no group statistic. One event cannot separate sympathy from common exposure; say so.

## Hands off to
`rotation-swap-decision` (group-relative signal only if group betas match).
