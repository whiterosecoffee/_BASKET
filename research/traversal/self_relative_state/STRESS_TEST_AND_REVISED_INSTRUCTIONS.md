# B06 #154 — Stress test, incremental-value gate and revised execution instructions

**Status:** research critique and next experiment specification, not an implemented trading signal or canonical data contract. Source: NVDA November 4 descriptive pilot in this folder; PR #160, B06 PRs #109/#145/#150, B17 PR #101, B07 issue #93, B00/B02 issue #148.

## Original learning objective versus actual demonstration

Original objective: identify self-relative ticker regime, distinguish price level from trend/volatility/participation, compare comparable historical episode trajectories, and determine whether these additional dimensions explain future continuation/failure/reversal better than already observed B06 traversal.

NVDA demo achieved: 526 Massive-adjusted daily bar retrospective NVDA/QQQ retrieval, SMA10/30/200, 5-session MA slopes, empirical prior-252 rank and synchronized raw ratio-relative returns as of 2026-11-04. Reported NVDA 200D deviation -2.219%, 30D five-session slope -1.429%, 200D slope +0.262%, 200D distance percentile 1.98, and 30-session NVDA/QQQ relative -4.94%. Two effectively distinct old analogue episodes remain far too few for inference. No B06 traversal-only versus +slope paired experiment, no frozen event-label manifest, no strict as-of revision replay, no ticker-local derivative or B02 source bar persistence verification.

**Decision:** The demo establishes descriptive measurement, not incremental classification or trade performance. The next experiment should not fetch additional price data until owner-approved persistence is addressed. Exclude retrospective-November label tuning.

## Research stress-test matrix: failure mode → required gate

1. **Moving-average support fallacy:** MA200 displacement/percentile is not resting liquidity or reversal evidence. Compare response after MA crossings conditional on predeclared slope, approach velocity and range state; label candidate contact vs actual accepted/failed break independently.
2. **Denominator/data snooping:** 11 overlapping qualifying days from ~two episodes do not yield 11 independent analogues. Freeze episode onset/end/refractory interval and resolution horizon; group overlapping candidates and use independent event counts, censoring and effective sample size. Report no probabilities for insufficient support.
3. **Added-feature illusion:** A +slope model can look superior simply because it alerts fewer times or changes the eligible cohort. Hold exact event IDs, as-of cutoffs, labels, split, candidate count, alert budget, training procedure and evaluation clock fixed. Pair traversal-only B06 #109/#145 controls with precisely one additional SMA30 five-session slope feature, then test remaining features individually.
4. **Clock and look-ahead:** Daily completed-session MA cannot be injected into a 10AM intraday signal using same-day final close. Use prior completed session only until the session completes; source available_at/revision must be <= decision time; source retrieval on Nov4 cannot imply availability in March.
5. **Adjusted-price mismatch:** Split/total-return settings, dividend, ADR, corporate actions and provider revisions must remain homogeneous across indicator and outcomes, with immutable manifest/version. A retrospective adjusted-price series can contain corrections unavailable at historical decision time.
6. **ATR/units:** Pilot reported simple mean true range, not contract's Wilder ATR14. Distinguish percent, percentage points, price units, ATR units; specify seeds/ties/zero-denominator and MA200 warmup. Do not silently substitute algorithms.
7. **Market attribution:** NVDA/QQQ ratio return measures relative performance, not beta-neutral excess return. B17 owns sector/factor context; estimate rolling beta strictly on prior observations and report missing/nonstationary model if insufficient.
8. **Regime transfer and nonstationarity:** Current conditions may lie outside past support; 200–500 sessions contain few independent crises. Predeclare time/volatility/regime stratification only when n supports it; abstain on sparse strata. Examine negative controls (shuffled feature, lagged-irrelevant comparator) and conditional return vs unconditional distribution.
9. **Causal opacity:** Volume near a price does not prove absorption; aggregated OHLCV cannot identify signed aggressor activity or exact volume-at-price. Keep market microstructure features unknown absent entitled trades/quotes; use B06 observed range and turnover as descriptive evidence only.
10. **Operational data loss:** Massive scratch workspace is not durable storage. Run approved B02 resolver inventory before fetch; after retrieval validate and persist source observations plus revision hash to owner-maintained store, verify cold replay. If no authorized destination, mark NOT_PERSISTED, preserve analysis/provenance and route existing #148/#136, without writing duplicate bars to B06.

## Prior-art families and mechanisms

- **Lo–Mamaysky–Wang systematic technical recognition:** replace visual chart matching with predeclared pattern definitions and compare conditional versus unconditional distributions; evidence of possible increment is market/context-specific, not proof for NVDA.
- **Time-series momentum / moving-average slope:** separate current displacement from change of baseline (slope) and its persistence across horizons; do not infer causation or near-term reversal.
- **Statistical process control and robust ranks:** map a deviation into ticker-specific distribution with sample counts/ties; extreme ranks identify rarity, not positive expected returns. Use volatility normalization with a declared ATR algorithm and comparable regimes.
- **Auction/market microstructure and volume-impact research:** use observed turnover and path efficiency to describe traded participation; signed flow/absorption and exact volume-at-price require appropriate trades/quotes; avoid causal support labels.
- **Event studies, survival analysis and censored outcomes:** episode IDs and time-to-event outcomes prevent repeated sessions from inflating samples; distinguish resolved, unresolved, competing first-breach/reclaim and same-bar ambiguity.
- **Purged chronological cross-validation and regime robustness:** train/test separation by episode/date with embargo across overlapping outcome horizons prevents leakage; report date-block intervals and stability across ticker/time, not random-row holdout.
- **Bailey et al. backtest overfitting and Harvey–Liu–Zhu multiple testing:** feature proliferation and threshold search inflate apparent significance. Register tested candidate count, simple baseline and corrections; do not tune on selected November decline.
- **Ports/adapters, design by contract, bitemporal event sourcing:** reuse B02 resolver/history and B06 traversal providers; point-in-time availability/revision/adjustment contracts define what may be compared. Separate source facts, derived features, model version and outcomes.

Research pointers:
- Lo, Mamaysky & Wang (2000), NBER w7613, https://www.nber.org/papers/w7613
- Bailey, Borwein, López de Prado & Zhu, Probability of Backtest Overfitting, https://scholarworks.wmich.edu/math_pubs/42/
- Harvey, Liu & Zhu, ...and the Cross-Section of Expected Returns, https://www.nber.org/papers/w20592

## Proposed acceptance ladder (lowest complexity first)

**Gate A — provenance and durable retrieval:** B00/B02 #148 approves NVDA/QQQ source resolver (or explicit private local NVDA pilot), verifies 200–500 eligible completed daily sessions with original endpoint/adjustment/calendar/availability, immutable raw/revision hashes, gaps, dedup and cold restart. Never claim the Nov4 526 bars persisted unless actual owner receipt exists. B14 ticker analysis destination via #136. Block and abstain if unavailable.

**Gate B — deterministic daily calculator contract:** B00 #103 accepts or rejects exact SMA10/30/200, 5-session slopes, Wilder ATR, rank/tie/min-n and consecutive persistence conventions; B06 #108 implement only after approval. Unit fixtures: 9/10, 29/30, 34/35, 199/200, 204/205, 451/452 valid session boundaries, split-adjustment continuity and missing/corrected sessions. Outputs explicit null and method IDs.

**Gate C — frozen historical episodes:** B06 #144 freezes discovery-time event boundaries/labels, continuation/failure/reversal definitions, resolution horizon, ambiguous-bar handling, censored cases, calendar and evaluation clock. Minimum n is a policy decision; default to descriptive-only when independent episodes too few and report n.

**Gate D — incremental paired baseline:** B07 #93 compares same frozen eligible episodes at equal alert count for B06 baseline against exactly baseline+SMA30 slope. Chronological training/holdout/purge, date-block bootstrap, precision/recall/false-reversal/delay, adverse excursion and false-positive counts; record negative cases. Only if improvement robust consider ATR-normalized distance, persistence, historical rank and B17 context individually.

**Gate E — decision utility (separate):** If user wants actionable trimming/reentry, evaluate transaction costs, missed rebounds, adverse excursions and sensitivity with point-in-time rules; do not equate better classification with profitable strategy. B01 #98 independently verifies exact SHA, tests and no relaxed strict checks.

## Instruction improvements to preserve

For any future self-relative ticker analysis:
1. Inspect canonical owner-approved local ticker history, session/adjustment/revision coverage and research file first. State source, cutoff, eligible count and missingness.
2. If an entitled Massive fetch is necessary, persist to approved B02 storage and verify receipt before calling it canonical; otherwise mark NOT_PERSISTED and route #148. Never silently drop a retrieval.
3. Compute strictly completed-session, versioned 10/30/200-day indicators only when sufficient history. Quantify short/medium/long disagreement, conditional unusualness and market-relative context without claiming support or probability.
4. Present **observation → relative historical position → independent comparable episodes → conditional outcomes → what incremental feature changes versus B06 baseline → falsifier**. If any gate absent, mark the corresponding field NOT_TESTED/UNKNOWN; don't fill with narrative confidence.
5. Use freeze-before-outcome, same cohort/alert budget, chronological purged holdout and a negative control. Count episodes, not just qualifying sessions.
6. Separate descriptive research from event classifier validation and from executable trade policy. Production/ticker-local outputs remain under owner-approved folders. Write substantive research under ticker-home by B14 and technique studies under B06; link without duplicating raw bars.
7. State one next executable owner action, no new framework, issue or branch, and no merge without approval.

**Current result:** NVDA descriptive demonstration successful; independent predictive/discriminative lift unverified; source retrieval not proven durably persisted or ticker-local; owner handoffs remain #148/#136. A negative or unsupported result is a valid outcome.
