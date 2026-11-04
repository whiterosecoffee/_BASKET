# READY-TO-PASTE — _BASKET B00/Codex orchestrator: consolidate B06 historical battle recognition

**Source owner:** B06 issue [#144](https://github.com/whiterosecoffee/_BASKET/issues/144), branch `work/144-october-compression-stress`, draft [PR #145](https://github.com/whiterosecoffee/_BASKET/pull/145). **Decision:** primary goal `recognize`; first acceptance evidence `historical`. This is an orchestrator intake/handoff, NOT permission to change other workers' files or an instruction to duplicate #144 as another implementation. If an entirely new conversation is launched, it must bootstrap a new unique issue/branch under AGENTS.md.

## Desired functional result
A **minimal reusable battle-range transition detector** consuming immutable, point-in-time canonical observations and emitting derived, append-only state changes. It must distinguish directional expansion, two-way chop, provisional absorption, stabilization attempts, failed defense, continuation, local reversal and unresolved cases **without using future events to label the present**. Nested price ranges are separate views over the *same* observation identities, not separate raw market stores. No prediction score, optimizer, continuous feed or user trading recommendation is part of #144 acceptance.

## First do reconciliation, not new architecture
1. Inspect authoritative GitHub main, AGENTS.md, sparks.json, active changed files, exact head and test evidence of: #144/PR145; B06 #108/PR109 and #149/PR150; B06 #154 (isolated self-relative trends); B10 #95/PR99 event journal; B17 #100/PR101 market context; B00 #148/PR147 ticker migration; B02 #151/#152 data quality; B07 #93; B01 integration. Do not misinterpret a draft PR as integrated or tests as executed.
2. Ratify one **consumer/producer** path: B02 produces canonical ticker source IDs and quality/freshness; #108 owns the canonical engine adapter; #149 provides synchronized cross-asset geometry; #144 supplies researched event semantics and falsification evidence; #154 tests incremental moving-average value; B17 supplies contextual factors; B07 calibrates; B01 validates exact-head; B08 alone handles deployment. Do not duplicate B10 PR99's polling/journal or create a parallel engine in this worker.
3. B00 decide the destination/ownership contract for ticker-local *derived* battle-event JSONL and how it is indexed. B06 #144 may document proposed events and source pointers but not write to `_TICKERS/**`, `tickers/**`, `runtime/**`, `schemas/**`, `engines/traversal/**` or shared CI. The existing single logical resolver `resolve(instrument_id, data_kind, access_mode, as_of)` is the required path. `_TICKERS/{ticker-symbol}` migration is **not verified completed**, so no silent fallback to legacy paths or raw-row copies.
4. B02 #152 has measured anomalies in fractional volume and some minute VWAP values outside high/low. Require a documented quality policy and complete RTH coverage manifest before claiming dollar-notional or volume-at-price accuracy. For missing ticker-symbol.jsonl intervals submit requests to B00/B02 with symbol, UTC interval, timeframe, provider, reason, test, and target; B06 never appends fabricated or duplicated source rows.

## Current #144 owned artifact — don't recreate
`research/traversal/october_2026_compression_stress/README.md`: authoritative minimal specification and A1-A8 gates.
`research/traversal/october_2026_compression_stress/ACCEPTANCE_CASES.md`: synthetic negative-test matrix T01-T16 and historical cohort/falsification design.
`research/traversal/october_2026_compression_stress/CANONICAL_TICKER_DATA_DEPENDENCY.md`: strict no-duplicate ticker data/missing-lines handoff.
Other documents under this one research subtree are time-stamped observational evidence and prior-art notes, not additional competing specifications.

## Acceptance-driven sequence
**Phase 1: historical recognition (B06 #144; exclusive research subtree only)**
- A1 Freeze battle boundaries at discovery; suffix replay must not change prior event IDs, boundaries or labels. Mark failure only on first knowable completed breach.
- A2 Exercise successful defenses, false absorptions, repeated failed rebounds, unresolved/censored attempts, ambiguous same-bar high/low, and local-vs-parent trend conflict.
- A3 Verify signed return, volatility-normalized velocity, USD/min turnover, signed bp/USD billion proxy, gross/net path efficiency, and same-clock baseline or explicit null. Signed OFI/depth is null without entitled trade/quote data.
- A4 Overlapping/child ranges reference original source IDs, count underlying turnover once and remain deterministic on replay/correction.
- A5 Replay full eligible October RTH cohort including failures; document November 2 and November 3 as historical/descriptive until genuinely pre-frozen out-of-sample tests exist. No cherry-picked examples.
- A6 Enforce B02 data anomaly, entitlement, auction, split/correction, timezone/DST, completeness and freshness gates.
- A7 Compare against price-only ATR/VWAP/volume baseline; report events denominators, false positives/negatives, missed rebounds, detection delay, right censoring, sensitivity by horizon. No fitted probability claims.
- A8 Publish source manifests, exact commit/test commands/logs, gaps and blocker statuses. Specified cases are not passed tests.

**Phase 2: integrate existing owners (ONLY after Phase 1 acceptance)**
- B00 arbitrate event schema, canonical resolver and exact derived event destination; link explicit handoff to B06 #108, B02 #152/#148, B01, B07 #93 as applicable.
- B06 #108 adapt the accepted detector to the existing range engine, using #149 geometry and B17 context by typed interfaces; no second store, no duplicate poller. B06 #154 contributes incremental trend features ONLY if historical tests demonstrate value.
- B01 independently verify exact SHA and source/migration tests; B07 later tests calibrated predictive value; B08 runtime remains separate.

## Required orchestration reply
Produce a short `basket.worker_resolution@1`-compatible report:
- objective, spark B06, source issue #144, draft PR #145, existing branch, exact owned paths;
- A1–A8: specified/passed/failed/blocked/not_run, with test evidence URLs, code SHA, input manifest hashes;
- dependency table with issue/PR, exact receiving owner/path, action requested, acceptance and unblock criteria;
- an ordered release/integration path reusing existing workers, and explicit pending gates;
- next executable step and any newly created handoff issue URL. **Do not call a receiver started merely because it was mentioned or an issue created.**

**End state:** We can describe whether a historical price battle was expanding, choppy, defended, failed or reversing with reproducible point-in-time events and known uncertainty. Only afterward pursue trading-entry ranking and any probabilistic inference.
