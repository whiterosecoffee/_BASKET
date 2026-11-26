# NVDA daily history recovery — 2026-11-04

Worker B14 #185; branch work/185-nvda-daily-history-recovery. Main contract pinned to b4910122a4c3f6ade747f2e4d59bd2d2e84b3c95. Evidence only; no canonical data-plane or resolver edits.

## Live-tape operator entry point

Start with [Live-tape analysis prompt](LIVE_TAPE_PROMPT.md), then use the [battle-range runbook](BATTLE_RANGE_RUNBOOK.md) and [read-only tape matrix](tape_matrix.py). Example: **Analyze live tape for NVDA, regular session, as of now, with SMH, QQQ and SPY as comparators.**

Read the [project operating contract](../../../../AGENTS.md), [worker protocol](../../../../orchestration/WORKER_PROTOCOL.md), [spark registry](../../../../orchestration/sparks.json), and [version policy](../../../../architecture/VERSIONING.md) on current main before changing system behavior. Reuse the existing B02 writer and B06 traversal contracts. Canonical integration is tracked in [#204](https://github.com/whiterosecoffee/_BASKET/issues/204).

**Read local daily JSONL first. Backfill missing observations through Massive. Always append newly queried evidence to the correct daily partition through the authorized writer and verify replay before calling a refresh complete.** Use separate approved schemas for bars, trades, quotes and derived evidence. If writing is blocked, report the exact gap or staging result. Keep provider data out of Git.

## Result

Eight New York session-date partitions: October 26–30 and November 2–4. Total 7,437 minute bars. All dates have 390 regular-session minute observations. November 4 ends at 23:08 UTC / 17:08 America/Chicago and is partial extended-hours coverage. Full capture metadata, per-file hashes, counts and flags are in manifest.json. These are minute aggregates, not individual trade ticks. One session date may cross UTC midnight after the November DST change.

Original source remains unchanged. The first recovery ZIP is retained. Its newly generated November4 IDs used source-key hashing rather than the main adapter's full-record hash; v2 corrects those IDs without changing bar values. October's 4,690 original records retain their IDs and economic contents; daily serialization differs in whitespace. Conservative availability bounds are retrieval/normalization times, not recovered original publication times. All bars are USD, unadjusted, TTD zero for current-use purposes.

## Validation

Reused main runtime/ticker_data.py and observations.py; did not implement a new repository store. Every daily partition: strict main input-schema validation, persisted canonical-ID verification, create followed by unchanged retry, successful as-of replay and identical replay record IDs. Zero duplicate source IDs. Main domain suite: python -m unittest discover -s runtime -p 'test_ticker_data.py' -v, 28 passed on fetched pinned source. Initial import failed for missing jsonschema; after installation 26 passed and two fixture checks failed because the partial checkout omitted unchanged dependencies. Fetching the main daily schema and revenue fixture yielded 28/28. No tests disabled. No new production code; independent CI not yet claimed.

VWAP outside OHLC: 1,286 observations retained with separate quality sidecars in the package. This is a review flag, not proof of corruption: provider trade eligibility/correction rules require B02 verification. No forward fill, fabricated prices, arbitrary VWAP clipping or silent correction. 390 counts are structural checks, not independent exchange-completeness proof.

## Retained data

Package NVDA_daily_history_2026-11-04_v2.zip; SHA256 c2deed54c653ba2beb5889941b331f027e1e694c9319e90d084a480256cea82e. Native file ID libfile_f2413974a85c8191ace2718228f601c0. Retrieve in the same user's authenticated Library; do not assume another agent or public reader has access. ZIP contains daily JSONL, quality sidecars, manifest and raw November captures. Raw licensed market data deliberately not committed to public GitHub.

## Existing owner handoff — ready to paste

Receive recovery #185 under B02 #11 and B00 #148/#183; coordinate quality #152 and B06 #108. Read current main AGENTS.md, sparks.json, runtime/TICKER_DATA.md and current owner evidence. Reuse integrated ticker_data adapter; inspect active changes and secure disjoint ownership before writes. Retrieve the v2 retained package through an entitled, authenticated route; verify ZIP SHA and every manifest file hash. Validate each row excluding persisted record_id as adapter input, then verify full-record canonical IDs. The existing adapter accepts one journal per explicit root; do not concatenate daily partitions into a multi-day target or bypass the one-day rule. Have B00 approve single-target session-date routing and compatibility; B02 implements only allocated runtime and ticker paths, B01 independently checks exact-head replay, deduplication, DST and one-day enforcement. Preserve original and v1 records, distinguish partition exports from installed source, retain VWAP flags pending provider reconciliation. Before ingestion, reconcile existing logical source keys and use explicit corrections with expected heads where economic values differ. Report partial November4 coverage and conservative availability; never claim a live feed or main integration from this receipt. Do not merge without authorization.

Dependencies remain existing owners; this issue creates no competing runtime implementation. Next owner action: B00/B02 reconcile this evidence into #148/#183's daily resolver and ingestion acceptance.


## Maturation increment

See [MATURATION.md](MATURATION.md) for the 13-dimension scorecard, ordered owner-specific roadmap, NVDA mechanisms, small research contracts and existing-owner receiver prompts. Machine-readable sequence: [maturation.json](maturation.json). The research-local [audit.py](audit.py) checks retained exports; it is not an ingestion writer or approved shared contract. [test_audit.py](test_audit.py) has 30 synthetic boundary tests. [audit-results.json](audit-results.json) records the real v2 package run: structural qualification with warnings, no hard errors; 1,286 VWAP review flags preserved. Main's separate ticker adapter suite previously passed28 tests. Shared PR CI does not by itself establish execution of these research tests. No forecast capability, production routing or new live service is claimed.


## Provider eligibility follow-up

[QUALITY_POLICY.md](QUALITY_POLICY.md) supersedes the blanket quality-blocker interpretation: Massive documents that volume/VWAP and OHLC use different eligibility sets, and fractional volume is normal. Preserve the flags without treating them alone as errors. Research checker0.2.0 now reports session counts;32 tests pass locally. Actual capture:34 regular-session flags across3120 bars and1252 extended-session flags across4317 bars. Exact volume at $200 remains unavailable from minute aggregates. Earlier frozen-source counts remain separate vintages. No canonical production acceptance or trade-level reconciliation claimed.
