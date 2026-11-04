# _BASKET B06 #154 — Broad improvement plan with bounded execution gates

**Status:** proposed cross-domain program, with B06 research sequencing and contracts committed here; **not** project-wide authorization to mutate other owners' files. Applies the user's request to make the historical-state tool broadly more useful and to proceed with low-risk, owned improvements. The existing B06 worker is #154 / branch `work/154-self-relative-historical-state` / draft PR #160. Do not create a duplicate B06 engine, issue or branch. No merge/release without explicit approval.

**Evidence refreshed:** 2026-11-04 GitHub main governance and spark registry v1.6.0; draft PR #160 still open and research only; PR #147 proposed 291 `_TICKERS` scope folders but is not merged; B00/B02 #148 migration open; NVDA local store #139/PR140 is merged and NVDA-only resolver PR173 is merged, **not a full multi-ticker source resolver**. The 2026-11-04 NVDA descriptive pilot and `STRESS_TEST_AND_REVISED_INSTRUCTIONS.md` in this branch are research evidence, not strict PIT-replayed, validated prediction or source-data persistence proof. No Massive fetch was performed to write this plan.

## Target product behavior

For every ticker, the tool must distinguish five outputs and their evidence gates:

1. **Descriptive state** — multi-window trend position, historical rarity, volatility regime, persistence, price/volume traversal, and aligned market-relative context with source, timing, method and missingness.
2. **Change detection** — frozen, traceable events (candidate approach, failed stabilization, accepted break, continuation, reversal candidate), explicitly distinct from definitive market microstructure absorption.
3. **Conditional historical outcomes** — nonoverlapping comparable episodes, counts and censoring, conditional return/drawdown/duration distributions, counterexamples and measurement uncertainty.
4. **Incremental-value audit** — which new state feature improves held-out event discrimination beyond baseline price/turnover/path evidence, with an identical eligible cohort and alert budget.
5. **Decision utility (separately gated)** — after demonstrated classification value, costs, missed rebounds, execution latency, adverse excursion and sensitivity tests before any trading recommendation.

An indicator is admitted only if its information is nonduplicative, temporally valid, reproducible and demonstrably useful over a simpler control. Descriptive metrics need not meet predictive promotion criteria but must be labeled descriptive.

## Priority and dependency schedule (milestones are evidence gates, not promised dates)

| Phase | Priority | Owner / existing destination | Deliverable and dependencies | Acceptance / blocker |
|---|---|---|---|---|
| 0. Data custody | P0 correctness | B00/B02 #148; reuse merged NVDA pilot #139/PR140, PR173; B01 CI | One approved instrument+venue resolver and entitlement-aware prefetch local coverage check. Any Massive fetch must be validated, durably written atomically or staged as NOT_PERSISTED, deduplicated and replay-tested. Separate original session date from retrieval/available/ingested dates, retain raw/adjusted policy, corrections and hashes. B14 #136 gets ticker-local analytical record. | Fetch existing coverage first; repeat fetch zero duplicates; power-loss/restart replay; exact count/gap/manifest and source hashes; no unapproved B06 market store, no silent data loss. **Current NVDA+QQQ 526-day captures not verified persisted.** |
| 1. Minimal deterministic daily-state core | P0 | B06 #108 for engine; B00 #103 for shared interface; B06 #154 for research contract | Single composable pure calculation over completed eligible daily bars. SMA10/30/200, five-session slopes, cross-window disagreement, consecutive persistence, Wilder ATR14 and optional past-only empirical rank; source/method/null outputs. Reuse #109/#150, no new ingestion or 3rd traversal engine. | Synthetic arithmetic fixtures: 9/10,29/30,34/35,199/200,204/205,451/452 warmup; split-adjustment, DST/holidays, as-of revision, missing bar, tie rules, units and zero denominators. Strict 252-prior rank is optional when <452 closes, not manufactured. |
| 2. Frozen event ontology and coverage | P0/P1 | B06 #144/PR145 and B10 #95/PR99 | Event IDs, prospectively frozen episode boundaries and labels, onset/confirmation/resolution, ambiguous bar order, refractory and censoring rules; no post-outcome episode selection. | Golden fixtures include defended/failed levels, false reversals, overlapping episodes and unresolved events; an eligible episode is an independent observation, not each qualifying session. |
| 3. Paired incremental evaluation | P1 | B07 #93 with B06 #154/#144, B01 #98 | Compare **same #109 traversal/turnover/path features** against same baseline **plus only prior-completed-session SMA30 five-session slope**. Same episodes, timestamp, horizon, label, splits and alert count. Chronological purged/embargoed holdouts, grouped date-block uncertainty, negative controls. | Per-class independent n, precision/recall, false reversal confirmations, delay, censoring, MAE/MFE, lift with uncertainty. No implementation of additional features unless the first comparison is interpretable; zero/negative/inconclusive is a valid result. |
| 4. Broader conditional historical context | P1 | B07 #93, B17 #100/PR101, B06 #108 | One-at-a-time ATR-normalized distance, persistence, historical rank, approach velocity, event duration, market/sector-relative context (not falsely described as beta-neutral). Evaluate coherent regime cohorts; optional time-to-event survival analysis. | Incremental held-out value at equal alert coverage and nonoverlap; effect remains when conditioning on baseline, across dates and where n allows across instruments; report insufficient coverage. |
| 5. Decision-relevance gate | P2 | B07 calibration #93, B06 #108, B17 #100 | Translate validated state to falsifiable descriptive scenarios only; consider trade rules separately. Costs, slippage, missed rebound and execution latency, adverse excursions, liquidity, sensitivities. | No quantified trading odds/automated advice until B07 independent point-in-time walk-forward proof; all alternatives and failures retained. |
| 6. Delivery, ticker-home and quality observability | P2 | B00 #103/#148/#136; B14 for NVDA; B01 #98; B08 existing services | Reusable per-ticker report/API that reads approved stores and links dated source evidence and analytical model hash. Compact state and data-quality panels, no duplication of ticker snapshots; explicit status: VERIFIED_SOURCE, DESCRIPTIVE_ONLY, NOT_TESTED, INSUFFICIENT_HISTORY, NOT_PERSISTED, STALE, UNRESOLVED. | Cold-read creates same result from frozen source+config+commit; ticker-local result exists in owner-approved destination, linked to B06 method, without raw data duplication; CI test suite tied to exact deployed contract. |

**Execution order:** phase 0 correctness blocks any *new* Massive fetch without a durable authorized sink and blocks strict PIT replay; phase 1 can proceed on **synthetic B06-owned fixtures** after B00 contract arbitration; phase 2 can specify test cases before market-data integration; phase 3 depends on source manifests and frozen episodes; phases 4–6 are conditional. Parallelize independent research design only, not conflicting file edits. No implied activation of other conversations.

## Necessary black-box interfaces (proposals; B00 acceptance required)

### Source/history port (B02 provider-independent read)
`resolve(instrument_id, data_kind="completed_daily_bar", access_mode="read", as_of)` -> instrument/venue/currency, adjustment policy, completed sessions, source IDs, event/effective time, first_available_at, observed_at, ingested_at, immutable revision IDs, input manifest hash, entitlement, TTD and explicit gap/quality state. Do not make hindsight-adjusted bars indistinguishable from source-available-as-of originals.

### Source write receipt (B02)
`persist(source_batch, expected_head, retrieval_time)` -> durable receipt containing dataset destination, accepted/duplicate/revision/rejected counts, immutable hashes, committed checkpoint and cold-replay validation. Failure returns NOT_PERSISTED, and any downstream state has a noncanonical warning. Do not call a scratch workspace or documentation summary a durable source store.

### Daily-state pure transform (B06)
`compute_state(instrument_id, completed_daily_history, as_of, method_version, config)` -> strict descriptive 10/30/200 features, denominators and null reasons, source manifest hash, model/commit hash, observational as-of status. **No provider polling, event ledger or probability estimation.** In intraday use, only the most recent *previously available completed daily session* is eligible.

### Episode and outcome ports (B06/B07)
`freeze_episode(observation_prefix, event_config_version)` -> stable event ID, boundaries, first-available evidence, candidate labels and unresolved ordering.
`evaluate_outcomes(frozen_episode_ids, eligible_followup, horizon_config)` -> independent event counts, resolution/censoring, follow-up distributions and uncertainty. B07 owns validation; B06 owns observed event morphology.

### Context and consumer ports (B17/B14)
B17 returns synchronized same-clock/series market-relative context, with separate beta-adjusted residuals only after pre-as-of beta estimation; B14 consumes dated derived NVDA reports and provenance references, not copied source bars.

## Testing and falsification matrix

| Invariant / failure injection | Expected result | Responsible owner |
|---|---|---|
| Missing, stale or conflicting local source, unavailable provider entitlement | Safe refusal/explicit missing; no invented bar, no falsely current state | B02/B01 |
| Duplicate fetch/retry, out-of-order revision, interrupted write, cold-restart | Idempotent durable replay; immutable revisions and counted correction | B02/B01 |
| Current intraday price with same-day unfinished daily candle | Prior completed daily basis only; no future close leakage | B06/B01 |
| Split/dividend adjustment discontinuity, currency/ADR mismatch | Reject mismatched series or annotate policy, exact source normalization | B02/B06 |
| Missing 200-session history / <452 strict 252-prior rank | Null feature with count and reason; no synthetic percentile | B06 |
| Fake historical support inferred from moving-average touch | No confirmed defense label without frozen independent event evidence | B06/B07 |
| One selloff yielding 11 qualifying sessions | Episode clustering; report independent n rather than 11 independent samples | B06/B07 |
| Different control/treatment event cohorts or alert budgets | Comparison invalid; do not publish lift | B07/B01 |
| Random-row train/test leakage across overlapping forward horizons | Chronological grouped purged split; holdout outcomes unseen in training | B07/B01 |
| Strong fitted result but weak out-of-sample or high false-positive rate | Reject predictive promotion; keep only descriptive measurement | B07 |
| Green generic repository validation but no domain replay | Mark domain unverified and block deployment/prediction claim | B01/B00 |

## Prior-art mapping — concrete, not automatic adoption
- Time-series momentum and moving-average family: cross-horizon slope/persistence versus distance. Falsifier: no paired discrimination conditional on #109 traversal.
- Statistical process control / robust empirical quantiles: source-qualified deviation percentiles with explicit past sample/ties. Falsifier: rank ceases to add information after normalized distance and regime stratification.
- Event studies and survival/competing risks: separate candidate onset, resolution, censored/ambiguous outcomes and time-to-recovery from repeated daily flags. Falsifier: apparent lift disappears when episodes are grouped.
- Microstructure and auction behavior: distinguish observed volume/turnover from causal signed-flow absorption. Do not claim dealer or institutional defense without entitled order/trade evidence.
- Purged chronological walk-forward, multiple testing and backtest-overfitting controls: prevent overlapping-label leakage and selection-driven performance exaggeration. Prefer fewer features with stable holdout value.
- Design by contract, ports/adapters, bitemporal event sourcing and idempotency: stop data duplication and let each owner provide a replayable interface; timestamp what was available, not what hindsight revealed.

## Immediate backlog, scoped action and coordination

**This B06 worker can finish now:** maintain this roadmap in its owned research path; preserve the existing descriptive NVDA pilot and falsification plan; keep #154/PR160 as the single B06 handoff. After B00 permits a stable input contract, propose a small standalone B06 core test through #108, not a new shared engine.

**Delegated cross-domain tasks already have destinations:** B00/B02 #148 (with source persistence and prefetch request already posted), B00 #103 (shared contract), B06 #144/#108 (episode/core), B07 #93 (validation), B17 #100 (context), B01 #98 (CI), B14 via B00 #136 (ticker-local research). Any required change must be made on the owner's branch. Recheck whether newer owner work has satisfied these before issuing another request; do not spam duplicate handoff comments.

**The next executable program action:** B00 resolves the canonical read/write adapter policy under #148 and accepts/rejects the minimal B06 daily-state API under #103, then B02 restores the missing NVDA+QQQ adjusted daily 2024-10-01..2026-11-04 source batch with verifiable receipts. With a source-qualified corpus B06 #144 freezes the historical episode cohort and B07 #93 conducts the paired experiment. If the corpus remains unavailable, run only synthetic, non-predictive calculator tests; no new Massive fetch without a persistence path.

## Orchestrator receiver prompt

> In whiterosecoffee/_BASKET, inspect current main, AGENTS.md, orchestration/sparks.json, B06 issue #154 / draft PR #160 and `research/traversal/self_relative_state/IMPROVEMENT_ROADMAP.md`. This conversation's controlling choices remain incremental measurable information, recent 200–500 completed daily sessions, and research-first handoff. Treat the roadmap as a proposed staged improvement program, not authorization to modify sibling domains. Verify active changed-file ownership. Keep #154/PR160 as the sole B06 research source and reuse #108/#144/#109/#145/#150 for existing traversal/event computations. First decide the B00 #103 minimal composed daily-state interface and #148 canonical B02 prefetch/persist/receipt path, including derived ticker home routing via B14 and #136; preserve the NVDA/QQQ 526 daily bar retrieval as **NOT_PERSISTED** until a verified B02 receipt exists. Assign phase 1 deterministic calculator + synthetic edge-case tests to B06 #108 within its own files after contract acceptance; phase 2 frozen episodes to B06 #144; phase 3 paired traversal-only vs +SMA30 slope held-out experiment to B07 #93; B17 #100 provides optional context, B01 #98 independent exact-head tests. Enforce same episode population and alert budget, no look-ahead, strict nulls, independent event counts and negative results. Prioritize data-integrity gates over feature proliferation; do not create duplicate engines/stores/issues, merge, release or claim live/predictive operations. Report exact issue/branch/owner assignments, accepted/deferred scopes, evidence hashes/checks/CI, blockers and the smallest next action.
