# P01 — Historical Self-Relative State

**Status:** previously implemented research and synthetic verification, not approved production. **Owner:** _BASKET B06 #154; production composition belongs to B06 #108. **Parent:** ../AGENTS.md and ../PURPOSES.json.

## Problem
Moving-average proximity alone cannot establish support or expected rebound. Determine whether price displacement, slope and persistence across horizons provide independent explanatory information beyond the already merged traversal metrics.

## Source implementation
Draft PR #160 / work/154-self-relative-historical-state at bbf8bc777c413d936a7c4e4c07489035980de997. Read reference_state.py, test_reference_state.py, RESEARCH_CONTRACT.md, PAIRED_REPLAY.md and NVDA_DESCRIPTIVE_PILOT_2026-11-04.md. Exact earlier 26-case hosted domain tests passed at 47bf50589159422312c337c1193da7ad14c742d0, workflow 44463053659. Later PR160 archival commit had successful named domain job but does not prove qualified historical lift.

## Input/output contract
Input: calendar-qualified, homogeneous split/total-return policy, one record per completed exchange session, bitemporal availability and immutable source manifest, as_of and algorithm version. Output: SMA10/30/200, 5-session slopes, price distances, signed run length, left censor, Wilder ATR14, past-only 252-value midrank requiring 452 closes for SMA200, missingness and method version. Pure read/compute only.

## Critical falsifiers
- A 1.98th percentile displacement is rarity, not rebound likelihood.
- Rising price may coincide with shrinking percent distance.
- A missing interior observation must not compress consecutive history.
- Daily slope must not use today's unfinished close during an intraday decision.
- Two historical episodes do not justify a calibrated market probability.

## Smallest next action
B00 #103 accepts or revises exact method and input cap. B06 #108 adopts the reference into canonical engine only after source-reader qualification. B07 tests incrementality under P04. No new historical-state engine.