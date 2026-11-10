# Broad Maturation Plan — _BASKET Market Intelligence, 2026-11-04

**Owner for this document:** B06 issue #155, branch `work/155-market-flow-watch-review`, draft PR #182. **Scope:** design/audit and only B06-owned pure event gate. GitHub main remains truth for implemented/integrated capabilities. B00 #136 is the dispatch authority, B00 #148 owns ticker migration, B00/B02/B01 handoff #183 owns one-day JSONL. This document DOES NOT authorize cross-domain changes.

## Assessment method
Scores are **engineering readiness heuristics** (not market probabilities, measured system throughput or claims of a release). Each dimension receives an evidence-qualified score from 0 (absent) to 5 (independently integrated and operational). Weighted contribution is weight × score / 5. Unverified or open draft implementation caps dimension at 2 unless another integrated main capability exists. Recorded design artifacts can earn governance score but cannot make a runtime operational.

| Domain | Weight | As-observed score /5 | Weighted /100 | Evidence and limitations |
|---|---:|---:|---:|---|
| Governance and issue/branch discipline | 10 | 3 | 6.0 | AGENTS.md, #136, #155, PR182; B00 queue present, integration incomplete |
| Instrument identity and canonical resolver | 8 | 2 | 3.2 | #148 migration and NVDA local pilot; full universe and alias migration unproven |
| Entitled capture and restart catch-up | 10 | 1 | 2.0 | B02 #11/PR15 and #151/PR153, not a persistent full-basket feed |
| One-day JSONL partition invariant | 10 | 0 | 0.0 | User decision #183; legacy multi-day journals contradict new invariant |
| Provenance, as-of and TTD | 8 | 2 | 3.2 | NVDA pilot replay acceptance, not system-wide quality |
| High/low + market vector calculations | 10 | 2 | 4.0 | B06 PR150 eight local tests reported; unmerged and no live registry consumer |
| Durable event qualification and notification | 8 | 1 | 1.6 | Current B06 pure gate unit-tested locally; no persistence/delivery integration |
| Breadth, weights and cross-asset synchronization | 8 | 2 | 3.2 | B17 PR101 source-sensitive context draft; weights often unverified |
| Earnings/valuation/entry bridge | 10 | 1 | 2.0 | B04 PR127 prototype, no full nine-company verified consensus |
| Independent cross-domain tests and CI | 8 | 2 | 3.2 | NVDA pilot B01 main acceptance; B06/B04 not independently integrated |
| Hosted runtime, durable alerts and SLOs | 6 | 0 | 0.0 | ChatGPT automation is not a hosted write-capable market ingest worker |
| Reproducibility, lineage and cost evidence | 4 | 3 | 2.4 | NVDA pilot source hash/replay, costs/effort and broader release not qualified |
| **Total** | **100** | — | **30.8 / 100** | This is a conditional engineering readiness assessment, not a 30.8% completion claim |

**Interpretation:** Design is relatively mature but source ingestion, daily partitioning, deployed delivery and independently verified integration gate actual utility. A local unit test does not raise operational scores.

## Dependency-ordered maturation roadmap
Each phase has a *smallest useful deliverable*, owner, acceptance and fallback. Plan is incremental; B00 must not change current global release priorities merely because a design document exists.

### M0 — Contract and freeze (B00; P0 dependency, before cross-domain storage writes)
- Adopt one-date-per-JSONL invariant from #183 and B00 security-master/path contract #148; assign instrument/session-date/venue/timeframe identity and late revision policy.
- List canonical consumer interfaces, existing PR changed-path ownership and no-dual-write cutover rules.
- **Exit:** a B00-approved versioned path/partition contract, explicit mixed-date rejection, owner assignments and migration archive strategy. **Fallback:** read-only legacy data with stale/mixed-date warnings; no production writes.

### M1 — Replayable data partitions (B02 and B01; P0)
- Reuse B02 journal #11/PR15 and minute-fetch #151/PR153; add date-keyed atomic writer only in B02-owned path. Trial on two adjacent CRWV sessions, then preserve/partition all existing multi-date CRWV/AAOI/SFTBY/NVDA records under approved resolver.
- Verify source IDs, original raw file hashes, supersedes chains, replay equality, missing periods, DST/calendar boundaries. Require 200+ sessions per eligible ticker as **distinct daily files**.
- **Exit:** B01 exact-head tests for two-day staged proof, zero loss/duplication, original archive retained and explicit rollout plan. **Fallback:** no cutover; keep legacy source readable.

### M2 — Pure market vectors and new extreme states (B06; B02/B17 read-only dependencies)
- Reuse PR150 market geometry, PR109 multi-range metrics and #155 market tracker. Take completed bars only; compute prior-close and prior-checkpoint % deltas, intraday and rolling 5/20/60/200-session high/low records, 5/15/30/60m displacement, range location and price-per-turnover (descriptive only).
- Mark missing bars, conflicting trade/aggregate, stale indices, invalid FX, unknown volume or duplicate Alphabet share classes as incomplete; null rather than inferred zero.
- **Exit:** deterministic golden fixtures, boundary/missing-session tests and explicit source-window labels; no forecast probabilities. **Fallback:** descriptive dated report only.

### M3 — Qualify alerts, avoid false regimes (B06, with B01 validation and B07 calibration)
- Prototype under `engines/traversal/market_watch_gate/**`: accepts confirmed external events; verifies evidence, freshness, time ordering, session status, synchronized requirements, dedupe against supplied prior event ID; fails closed. The gate does **not** define a confirmed market state nor own event journal.
- Reuse B10 PR99 event-journal mechanics only after B00 arbitration; prospectively freeze detector thresholds and hysteresis, then replay Nov 2–4. Compare alert count, duplicated episodes, detection delay and false confirmation to historical adjudicated labels. Without labels, report unknown.
- **Exit:** B01 independent exact-head tests for event suppression, correction/supersession and historical replay; B07 calibration before claiming predictive effectiveness. **Fallback:** no notifications and only observations.

### M4 — Ticker evaluator (B04 with B02/B03/B06/B17 inputs)
- Extend B04 #126/PR127, not a competing valuation engine. Nine issuers: NVDA/CRWV/COHR/MRVL/LITE/INTC/AAOI/CRDO/ALAB.
- Verify 2027/2028 calendarized GAAP/non-GAAP estimates, revisions, EPS/FCF, diluted shares, debt and EV; stress 10/20/30/40% multiple compression and earnings shortfalls; handle MRVL/LITE deal and CRWV financing separately.
- Entry status consumes B06 date-qualified market vectors READ-ONLY; valuation never equates drawdown with cheapness.
- **Exit:** three source-pinned issuer bridges + nine-row missing-data matrix + exact-head math/point-in-time tests; no unsupported numeric risk-adjusted winner. **Fallback:** incomplete rankings labeled provisional.

### M5 — Runtime and notification qualification (B08 with B02 and B01)
- Integrate only after entitlement, durable storage, checkpoint/restart replay and correction semantics are proven. No new automation until existing AI Market Flow Watch has been reconciled for delivery/cadence.
- Demonstrate silent unchanged state, one notice per material episode/lifecycle change, lag/TTD/market-closed behavior, runtime health and security controls. Store canonical data outside GitHub live repo.
- **Exit:** independently verified hosted dry-run and incident/recovery tests, operational owner and measured latency/cost/quotas. **Fallback:** scheduled manual/chat analysis with explicit current data limitations.

### M6 — Safe expansion and release (B00+B01+B07)
- Add high-priority tickers only after quality gates; include known ADR/index/fund/FX session rules. Validate point-in-time walk-forward/out-of-sample behavior, liquidity costs, missed rebounds and sensitivity.
- **Exit:** exact-head CI, post-authorized-merge main CI, explicit human review and release approval; no automatic merge/tag. **Fallback:** keep isolated experimental components.

## Validation matrix
- P1: one-date JSONL rejects cross-day rows atomically, including DST and overnight session boundaries.
- P2: replay late corrections by original event session, never ingestion date; old file SHA preserved.
- P3: 5/15/30m delta, 20-session turnover and price/volume efficiency remain descriptive and true to aligned data.
- P4: session-specific high/low and 5/20/60/200 completed-session extrema do not look ahead.
- P5: stale VIX / after-hours index, conflicting last trade vs minute close, timestamp gaps => `unknown` not confirmed event.
- P6: unconfirmed / repeated / immaterial / stale alerts suppressed; material after-hours supported only when verified.
- P7: B04 fiscal/calendar and diluted-share bridge, negative EPS and merger/financing cases.
- P8: B01 exact-head CI proof, B00 ownership review, and explicitly authorized integration.

## Evidence, effort and priority discipline
- **Quality over alert volume:** count evaluated event episodes, confirmed transitions, suppressed duplicates, explicit unknowns; never equate many notifications with effectiveness.
- **Token/effort budget:** first reuse exact existing files, then one narrow implementation/test, then independent verification; measure actual effort rather than inventing token savings.
- **Metrics to collect on each attempt:** issue/PR/commit, date, execution command, test output URL, changed paths, source fixtures, replay coverage, failure class, correction and remaining blocker.
- **Critical sequencing:** M0→M1→M2→M3→M5 for operational alerts; M0/M1 inputs→M4 for valuation. B06's offline gate may run independently, but production use must wait.
- **Do not** schedule new watchers, merge, rewrite legacy data, upgrade a shared schema or create new owner branches from this B06 design task.

## Codex receiver
Read this plan, #155/PR182, #183, #148 and #136, then current main and changed paths for B02 PR15/153, B06 PR109/150/160/168, B17 PR101, B04 PR127, B01 #129 and B08 PR55. Reuse components; collect issue claims for live owners and dispatch only the smallest unblocked work per owner. Keep cross-domain changes in separate receiver issues/branches. Report one next owner action and real test evidence. No merge.
