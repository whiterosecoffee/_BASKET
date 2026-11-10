# _BASKET B06 #154 — Maturation assessment, evidence-gated delivery plan and executed upgrades

**Current scope:** B06 research/reference only, issue #154, existing branch `work/154-self-relative-historical-state`, draft PR #160. This report does not supersede B00 shared contracts, B02 ingestion, B07 calibration or B01 CI. No merge authorization.

## Scope and evaluation target

We need more than chart proximity: (1) define reproducible completed-daily historical state, (2) show whether it is unusual relative to ticker's own history, (3) recognize comparable *independent* episodes, (4) evaluate whether those features change B06 classification beyond range/volume/path evidence, and (5) separately determine decision utility, all from source-provenanced point-in-time observations with durable storage.

**Product success:** an instrument-parameterized, read-only state projection with immutable source/model identity and missingness, a statistically defensible incremental-value result (including null/negative outcome), a ticker-home result, and CI evidence. Tool is not considered operational merely because documentation or reference math passes.

## Honest capability score (after research reference implementation)

Ordinal 0–5 per dimension, equal-weight for visibility only; no assumption that 1 score point equals an engineering milestone or that total equals percent completion. 0 absent, 1 documented gap, 2 designed/provisional, 3 isolated implementation with local tests, 4 independently contract-validated, 5 integrated and observed on qualified as-of data.

| Capability | /5 | Grounded evidence | Next evidence to advance |
|---|---:|---|---|
| Source custody, local-first fetch, durable as-of history | 1 | Massive 526-bar NVDA/QQQ pilot retrieved but NOT_VERIFIED_PERSISTED; #148/#183 open | B02 durable partition receipt and restart/replay, source/adjustment/gap manifest |
| Deterministic 10/30/200 feature math | 3 | Research-only `reference_state.py`, synthetic 19-case local pass | B00 accepted contract, B06 #108 production test equivalence |
| Point-in-time temporal discipline | 2 | Reference validates explicit availability cutoff, calendar attestation, prevents future-close; real revisions/calendar delegated | B02 resolved revisions and time-zone/session attestation on dated data |
| Frozen event morphology | 2 | B06 #145 research ontology, no complete frozen historical episode corpus | Prospective episode IDs, ordering, censoring, labels and chronological fixture |
| Incremental discrimination against traversal | 0 | Primary matched baseline-versus-+SMA30-slope historical replay NOT RUN | B07 same-cohort purged held-out test with independent episode n |
| Market-relative/factor decomposition | 2 | NVDA/QQQ adjusted ratio return observed, not beta-neutral; B17 #100 provider draft | Same-horizon, as-of market/sector residuals with independent benchmark method |
| Reproducibility and falsification | 2 | Synthetic exact-blob local tests, unverified historical replay | Frozen input/config/commit hash and historical negative/control cases |
| Modular reuse / ownership | 4 | B06 new research subtree, B00/B02/B07/B17/B01 ownership respected; #109/#145/#150 reused | B00 interface signoff, no overlapping engine, approved production consumer |
| Independent domain CI / integration | 2 | GitHub generic validation passed prior doc heads, local synthetic suite tested, not B01 acceptance | B01 exact-head domain suite and post-authorized-main verification |
| Ticker-local results / delivery usability | 1 | NVDA report committed in B06 methodology, not B14 ticker home; UI is not production | B14/B00 approved ticker-home pointer and compact status/evidence report |
| **Total (diagnostic)** | **19/50** | **Research mathematics now partially executable; decision value unproven** | Do not convert to “38% deployed” |

**Correctness overrides score:** unqualified source or look-ahead is a release blocker even if average rises. The separate November 4 audit of conversation execution quality (39/50) scored conversation process, **not this product**.

## Work ranking (illustrative 0–5 on reusability/impact/novelty/evidence/feasibility/risk reduction)

| Task | R/I/N/E/F/R | /30 | Owner | Why now |
|---|---|---:|---|---|
| Canonical Massive local-first read + durable one-session-partition receipt | 5/5/3/2/2/5 | 22 | B00/B02 #148/#183 | Critical data-integrity prerequisite; correctness priority override |
| Single approved pure daily-state port + conformance test adapter | 5/4/2/3/4/4 | 22 | B00 #103 then B06 #108 | Prevents a parallel calculator and standardizes missingness |
| Frozen episode labels and reproducible candidate corpus | 5/5/3/2/3/4 | 22 | B06 #144, B07 #93 | Required denominator for valid learning |
| Paired same-cohort incremental feature test | 5/5/4/1/3/5 | 23 | B07 #93 and B06 #154 | Determines whether slope deserves promotion |
| B01 exact-head conformance / replay CI | 5/4/2/3/3/5 | 22 | B01 #98 | Separates synthetic local tests from real domain evidence |
| B17 factor/sector residual and ticker-local UI | 4/3/3/2/2/3 | 17 | B17 #100, B14 via #136 | Valuable after verified source/core; avoid premature presentation |
| Hidden-state regimes, adaptive horizons, weighted scores and trade forecasts | 3/3/4/1/1/1 | 13 | Deferred, B07/B06/B00 if validated | Strong overfitting/coupling risk; no evidence to justify now |

Scores are *planning judgments*, not measured time/token savings. Implementation effort roughly low for pure synthetic calculation, medium for historical paired research, high for cross-domain migration, each uncertain until owner inventories current code.

## Sequence and acceptance (no cross-domain writes)

### Phase 0 — correctness/data before more Massive pulls (P0, external)
B00 #148/#183 approves actual resolver and exactly-one-exchange-session-per-physical-JSONL rule. B02 checks local source, retrieves only needed gaps, validates and persists adjusted/specified-bar revisions atomically, records effective/observed/first-available/ingested times, provider params, hash and durable checkpoint. Repeat fetch must be idempotent, cold replay equivalent; if no sink, NOT_PERSISTED. NVDA-only PR140/PR173 are reuse inputs, not full QQQ resolution. B14 via #136 records ticker-local *derived* NVDA research; B06 does not edit ticker entity folders.

### Phase 1 — smallest useful deterministic measurement (P0, executed as research reference)
Files in `research/traversal/self_relative_state/`:
- `reference_state.py`: **nonproduction pure oracle**, no API polling, no file writes, no market-data store; complete/available/as_of, adjustment, OHLC positivity, sorted sessions and caller calendar attestation; SMA10/30/200, slope_5, approach velocity in pp/session, signed consecutive persistence and left-censor, seeded Wilder ATR14, strict rank252 and NULL-before-warmup, cross-window spreads. No forecasting.
- `test_reference_state.py`: synthetic conformance suite (19 tests) for warmup 9/10,29/30,34/35,199/200,204/205,451/452, ATR14, ties/persistence/left-censor, source-cutoff, missing/completion, duplicate/mixed adjustment, naive clock and exchange-local-next-day availability.

**Local exact-blob verification:** Python 3 unittest discovery in `/tmp` (only synthetic tests), 19 passed/0 errors/0 skips; `python3 -m py_compile` passed. The executed source blobs were checked against GitHub blob SHAs of the two committed files: `reference_state.py` `c6e9b6cc473305bcea1d84732e84e3a879002267`, `test_reference_state.py` `1b6ec5ccc4b40ce64d3f3004ddb38ea57d87e3f0`. No B01 independent runner or historical backtest asserted.

**Failed-then-fixed lessons (do not erase):**
1. First run: 17/18 passing and one failed assertion incorrectly assumed that positive price slope necessarily increases percentage distance from a moving average. On a linear rising path, MA distance can *shrink* as denominator grows. Corrected expected sign; rerun 18/18 pass. **Rule:** cross-check dimension and algebra, not visual direction intuition.
2. UTC-date comparison initially excluded records whose exchange-local session date was later than UTC `as_of` date, even if explicit `available_at` was earlier. Corrected to use actual source availability cutoff, added exchange-date-leading-UTC test, 19/19 pass. **Rule:** do not compare exchange-local trading-day labels with UTC calendar date as a proxy for availability.

**What this does not do:** verify calendar; ensure missing exchange sessions are detected; resolve revisions, adjustments, dividends, venues or historical source licensing; prove market lift or trade utility. Caller must attest validated calendar and supply a true manifest. Research code must not be treated as canonical engine: B00 #103 approves a minimal interface first; B06 #108 can adopt/adapt the tested logic in its exclusive engine paths with independent tests.

### Phase 2 — event freeze (P0/P1, external B06 #144)
Reuse #145 event ontology and #109/#150 observed traversal definitions; freeze episode ID, creation/confirmation, same-bar ambiguity, break/reclaim ordering, follow-up horizon, censorship and refractory overlap rule before looking at outcomes. Use source replay from Phase 0; count **independent episodes**, not days.

### Phase 3 — paired incremental falsification (P1, B07 #93)
Fixed first comparison: same #109 range/turnover/efficiency baseline and identical baseline + only SMA30 5-session slope from last available completed daily bar. Same cohort, alert budget, labels, time, splits, training threshold policy. Chronological purged/embargoed holdouts; date-block uncertainty. Report independent event sample size, class precision/recall, false reversal count, delay, MAE/MFE, rebound costs if trade policy later specified. A negative result supports retaining simpler traversal. Do not tune on November 2–4 charts or infer probability from 1.98th percentile.

### Phase 4 — conditional expansion (P1, after measured effect)
Only if an incremental result is robust: add each of ATR displacement, persistence, prior-rank, approach velocity, B17 contextual residual separately; correct multiple searches, model instability and regime drift. Do not build hidden-Markov/adaptive regime forecasts solely on suggestion.

### Phase 5 — point-in-time operational consumption (P2, after B00/B01 gates)
Composable B06 descriptive state + B17 context + B07 outcomes, B14 ticker research pointer, readable per-ticker report with source/expiry, status, scenario triggers and explicit unknowns. B01 domain CI on exact head, authorized merge and main CI when appropriate; no continuous market data service claim from GitHub only.

## Black-box promotion criteria

1. **Source port** (B02): immutable one-session partitions and manifest/availability/adjustment validation; fail closed on source conflicts.
2. **State port** (B06): pure deterministic function, no networking, same result across replay and direct complete-bar input; method/commit/source hash and null reasons.
3. **Episode port** (B06): frozen, source-backed state machines with no hindsight mutation.
4. **Outcome port** (B07): independently evaluated conditional results, censoring and uncertainty, no unverifiable probabilities.
5. **Consumer port** (B14/B17/B08): references source and derived results rather than duplicating histories; only approved runtime displays current state.

## Exact next owner action

B00 #103 approves or revises the proposed B06 daily-state interface (research #154) and #148/#183 source/partition resolver. Then B06 #108 adopts the reference arithmetic without creating a competing engine; B02 data custody and B07 paired test remain independent owner stages. This branch supplies tested reference logic only. **No cross-domain file modifications, main commits, automatic merges, release tags or probability promotion.**


## Follow-up hardening — fail closed on missing interior sessions (2026-11-04)

**Observation:** the research oracle initially filtered unavailable/incomplete sessions before rolling features, potentially collapsing a missing interior daily session and treating noncontiguous observations as sequential. A caller's `calendar_validated=True` is not enough to make that compression acceptable when a supplied session is explicitly excluded. **Correction:** if an excluded/incomplete bar is followed by a later eligible bar in the supplied ordered series, `evaluate` now raises `ValueError("non-prefix eligible sessions; refusing to compress a history gap")`. An unavailable *tail* is still discarded without error; real exchange holidays not supplied as sessions remain the responsibility of the approved B02 calendar adapter. The change stays inside nonproduction B06 research code and does not claim a comprehensive calendar validator.

**Regression design:** `test_interior_unavailable_bar_fails_closed`, `test_interior_incomplete_bar_fails_closed`, `test_future_tail_is_excluded_without_compression`. These extend the original 19 synthetic cases to 22 authored tests; **execution of the new 22-case suite must be verified against the latest committed source**, and generic GitHub QC must not be described as domain test execution. No real historical replay was performed.

**Reasoning:** a hidden missing session can contaminate every subsequent SMA and percentile; explicit fail-closed behavior is preferable to plausible but numerically wrong state. The later production B06 #108 component should consume B02's calendar-qualified indexed partition reader under #148/#183 and additionally test gaps not represented by supplied rows.
