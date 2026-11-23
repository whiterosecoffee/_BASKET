---
name: rotation-universe-hierarchy
description: Defines the ticker universe and its nested groups (market, sector, peer group, name) for the rotation toolkit and reports coverage. Use when adding tickers to the basket, assigning peer groups, checking how many names are priced, or building the hierarchy used for group-relative and sympathy calculations.
compatibility: Reads universe/basket_manifest_work146_snapshot.json (read-only snapshot of branch work/146); writes only under B04 paths.
metadata:
  owner: B04
  version: 1.0.0
---
# Universe and hierarchy

## Facts to start from
297 identifiers = 291 manifest symbols + 6 additions (FLEX, HIMX, INOD, TTMI, IBIDY, CXMT-USD); 243 priced here. The user expects 300+, so the list is incomplete: ask for missing names, add them to `ADDITIONS` in `basket.py`.
Manifest `basket_groups` (convexity, general, previous, signals, screenshots, ...) are watchlist buckets, not economic groups. Peer groups live in `cohort/peer_groups_by_industry.json` and cover only 46 names.

## Hierarchy contract (target, not yet complete)
`hierarchy.json`: `market > sector > peer_group > name`, one parent per name, each peer group at least 3 names, group index defined (equal weight by default). Names without a peer group are listed as `unassigned`, never forced into one.

## Procedure
1. Load with `basket.load_universe`; count by `instrument_type`; list tradable names without bars.
2. Assign a peer group only from evidence (business description, revenue mix, filings); record the basis in the file.
3. Keep benchmarks (MSFT, SMH, QQQ) outside cohort statistics.

## Stop rules
Do not infer a group from the ticker list a user pasted; do not edit the manifest.

## Hands off to
`rotation-group-sympathy`, `rotation-relativity-ratios`.
