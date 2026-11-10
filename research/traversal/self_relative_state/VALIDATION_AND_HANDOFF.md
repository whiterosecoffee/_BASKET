# Validation protocol, worker extension routes and orchestrator receiver

Issue #154; B06 research-only branch. **Status at authorship: unexecuted empirical research.** Reading draft-source files verifies interface intentions; it does not verify runtime operation, main integration, or predictive performance.

## Incremental research experiment
**Pilot universe:** QQQ, NVDA, CRWV as feasible; eligibility and availability must be verified independently. CRWV may not have 200 or 500 eligible sessions; in that case explicitly report insufficient history and substitute a mature, predeclared ticker for a full 200D test while leaving CRWV's 200D null. Never synthesize a 200D value. Separate ETF versus equity corporate-action policy.

**Sample policy:** most recent 200–500 *available and eligible* completed daily sessions per ticker, obtained through the B00-approved resolver after #148, with as-of snapshots. Important caveat: full 500-session input history yields only ~301 200D observations and fewer after other feature warmups; event-cohort comparisons may be sparse. Restrict claims accordingly; expand beyond 500 only via a subsequent explicit scope decision, not as a hidden change.

**Baseline ladder, fixed before outcome inspection:**
- M0: unconditional same-ticker forward 5/10/30-session realized returns, with non-overlapping event subsets.
- M1: price distance to SMA200 alone; threshold/percentile bins fixed on training slice.
- M2: distance normalized by ATR14 plus SMA200 slope and persistence.
- M3: M2 plus 10/30 disagreement and approach velocity.
- M4: M3 plus pre-existing B06 traversal primitives (no duplicate price-volume code).
- M5: M4 plus B17 same-session-aligned market-relative/context features (no retrospectively estimated beta).

**Targets:** descriptive next-period return distribution, maximum adverse/favorable excursion (MAE/MFE), time to local stabilization under predeclared rule, failed stabilization frequency, realized drawdown and missing rebound cost. Censor events lacking a complete forward observation window; record exclusion counts. Never label an outcome available as of the event instant.

**Validation:** chronological expanding/rolling train-validation-test split; as-of data availability and gap/holiday rules; embargo or purging to control overlapping event horizons; threshold and feature selection only in training; uncertainty intervals with dependence-aware block resampling; stratification by market/volatility regime only if sufficient sample; sensitivity to 200 vs 500-session lookback and multiple-testing corrections. Null fields/insufficient samples must fail closed. Compare discrimination, calibration where relevant, false positives, detection delay and measured cost of missed rebounds. Report incremental lift against best lower-complexity model with uncertainty, not simply training accuracy. Include spread/slippage/fees only if evaluating tradable entry/exit rules.

**Promotion gate:** no score/probability or trade action from this research. Features may be proposed for B06 if held-out incremental value survives; B07 owns calibration before probabilistic use. Negative result is an acceptable finished result. A 200D average's visual role as support is a hypothesis, not proof of liquidity absorption.

## Current repository collisions and source evidence
- PR #109 already owns `engines/traversal/metrics.py`, `engines/traversal/run_metrics.py`, tests and `research/traversal/data-mapping.json`.
- PR #145 owns `research/traversal/october_2026_compression_stress/**`.
- PR #150 owns `engines/traversal/market_geometry/**`.
- PR #101 owns `engines/composites/market_context/**`; PR #99 owns `research/CRWV/trading-tool/**`.
- PR #147 establishes only proposed `_TICKERS` identity scope, not migrated historical bars; issue #148 is the existing migration handoff.
- This branch exclusively writes new `research/traversal/self_relative_state/**`; no code/shared schema/data/runtime/CI edits.

## Extension handoff matrix (reuse existing issues; no duplicate issues)
| Receiver | Existing issue / PR | Target owner's precise request | Completion evidence |
|---|---|---|---|
| B00 | #148 and #103/PR104 | Approve resolver and experimental feature interface, collision/sequencing arbitration; distinguish daily window from intraday range | Versioned interface decision, accepted owner paths, conflict-free integration plan |
| B02 | #148 and #61/PR15 | Provide complete and appropriately adjusted, point-in-time daily history 200–500 sessions, effective/available/ingested timestamps, correction/replay and explicit insufficiency | Immutable manifest, source dates, eligibility & gap counts, replay checksum |
| B07 | #93 | Design and run conditional outcome/event discrimination research, walk-forward test and multiple comparison control; no predictive odds without calibration | Exact event/feature cohort IDs, train/test boundaries, held-out metrics with sample sizes and errors |
| B17 | #100/PR101 | Expose daily same-horizon QQQ/sector-relative comparator with explicit clock/beta policy and point-in-time availability | Versioned input/output and aligned baseline test; null on missing comparator |
| B01 | #98 or related B01 CI handoff | Independently test agreed interface, insufficient-history behavior, as-of lookahead prevention, replay determinism and exact-head CI | CI run URL and exact head SHA, regression failures not masked |

**Coordination policy:** send targeted comments to existing owner issues where possible; none of these requests imply that another worker has accepted, started or completed the extension. B00 arbitrates any new cross-domain schema and new destination paths. If no suitable existing issue is available, open a linked handoff issue rather than modifying another domain directly.

## Ready-to-paste orchestrator receiver prompt

> Reconcile _BASKET B06 issue #154 and draft PR from branch `work/154-self-relative-historical-state` with active B06 PRs #109 (intraday ranges), #145 (compression/event research) and #150 (market geometry). The user's decisions are: primary objective **incremental information**, recent **200–500 completed-session lookback**, and **research-only handoff**. Do not create duplicate B06 engines, price histories, schemas or issue/branch. Read this branch's README, RESEARCH_CONTRACT and VALIDATION_AND_HANDOFF, compare actual changed paths and feature semantics, then decide whether to compose the proposed daily historical-state dimensions into B06's existing contracts. Resolve B00 shared interface and #148 canonical resolver first; coordinate B02 (#148/#61), B17 (#100), B07 (#93), B01 (#98) through their own issue/branch ownership. Pilot QQQ/NVDA/CRWV subject to verified source coverage; refuse synthetic 200D for insufficient-history tickers. Establish M0–M5 incremental benchmark and point-in-time replay; report negative results, missing samples, false positives and no untested trade probabilities. Preserve all existing draft PRs for evidence-based consolidation; no merge/release without explicit user authorization. Return owner/issue/branch map, dependency order, exact accepted paths, test evidence and next action.

## Known blockers
1. Canonical `_TICKERS` resolver and data migration #148 not verified complete.
2. Adequate point-in-time daily history (especially young CRWV) not yet proven for specified horizons.
3. Independent exact-head CI and held-out incremental empirical tests not executed for this research.
4. B00 must approve any eventual shared schema; this branch claims no production implementation.

## Research acceptance checklist
- [x] Scoped to owned B06 research subtree, no competing engine, no duplicated bars.
- [x] Source references and bounded baseline ladder documented.
- [x] Fail-closed insufficient-history semantics, look-ahead and survivorship caveats specified.
- [x] Cross-domain handoffs and receiver prompt provided.
- [ ] Actual source-corpus replay and M0–M5 held-out results (assigned downstream).
- [ ] Independent CI/evidence and B00 production contract acceptance (assigned downstream).
