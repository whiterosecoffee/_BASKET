# Experimental B06 self-relative state research contract

**Status:** design-only; not a canonical schema, implemented API, validated strategy or live signal.
**Consumer:** future B06 composition after B00 approval. **Source:** B02 canonical history and B17 context; no local shadow market data.

## Inputs and temporal invariants
- Instrument identity, listing/venue, exchange calendar and timezone; record regular versus extended session policy.
- Completed daily OHLCV with source class, `effective_at` (session), `observed_at`, `available_at`, `ingested_at`, correction/revision ID, provider, and as-of cutoff. Reject look-ahead, duplicates, impossible OHLC and nonmonotone timestamps; missing sessions are not zero-volume trading sessions.
- Explicit raw vs split-/distribution-adjusted methodology; no raw/adjusted mixing inside a return/MA/ATR series. Prefer a total-return adjusted reference if policy and vendor data permit, otherwise label price-return-only; dividends/corporate actions must not silently distort analogues. FX basis required for non-USD original venues.
- `as_of` and data-accessible-as-of semantics: for each replay instant, use only revisions available at that instant; revised historical prices must not be retrospectively presented as available earlier. Immutable input manifest hash, code/config version and Git SHA.
- **Recent eligible lookback 200–500 completed sessions**; report raw eligible count, MA warmup, percentile window available and analogue cohort count separately. A max of 500 data sessions yields at most 301 200D distance values, and fewer if slope/persistence warmup is required. `null` when sample insufficient. Avoid claims of a well-populated 200D percentile at a 200-session boundary.

## Feature candidates (daily only; no intraday duplication)
| Candidate | Exact conceptual definition | Failure / interpretation |
|---|---|---|
| SMA10/30/200 | Arithmetic mean of prior N **completed daily closes including the as-of completed session** (point-in-time); no partial current daily bar | Null if fewer than N valid sessions |
| MA distance | `close / SMA_N - 1` | Price displacement, *not* support or expected rebound |
| MA slope | `SMA_N(t)/SMA_N(t-k)-1`, predeclare k=5 completed sessions for trial | Null if warmup missing; do not confuse daily with intraday slope |
| Cross-horizon spread | `SMA10/SMA30 - 1`, `SMA30/SMA200 - 1` | Descriptive alignment only |
| Persistence | Number of consecutive *completed sessions* with close >/< SMA_N, equal handled by explicit tie rule | Null if unavailable or lookback truncated |
| ATR-normalized displacement | `(close-SMA_N)/ATR14`, using Wilder ATR14 on adjusted OHLC if consistently adjusted | ATR null for insufficient prior close/high/low; low-liquidity bars need quality gate |
| Empirical historical percentile | Past-only rank of current MA distance among available comparable prior values (ties use mid-rank); window max 252 or available valid observations, with n reported | For 200D, many early records have no rank; do not force a percentile or call rank a probability |
| Approach velocity | `(distance_N(t)-distance_N(t-k))/k` in percentage points per completed session | Different from intraday market geometry; may conflate MA drift and price drift |
| Market-relative context | B17-provided same-horizon benchmark-relative return or *pre-as-of estimated* residual beta model, explicitly labeled method | Simple return spread is **not** beta-neutral alpha |

For all features include `window_sessions`, `as_of`, `sample_size`, `data_quality`, `missing_reason`, `source_manifest_hash` and `algorithm_version`. Only emit measured values, or null. Numerical rounding for display must not contaminate event thresholds.

## Event ontology, deliberately composed rather than reinvented
Reuse B06 battle range and PR #145 event vocabulary: contact, tentative defense, accepted break, failed stabilization, follow-up resolution. A moving-average proximity candidate is *not* a battle contact unless the frozen event definition and its independent measurement agree. Predeclare proximity thresholds in ATR units; preserve every qualifying candidate including failures, with onset and resolution times.

## Experimental state snapshot (illustrative, all outcomes unknown)
```json
{
  "contract": "basket.self_relative_state.research@0",
  "instrument_id": "QQQ",
  "as_of": null,
  "frequency": "completed_daily_session",
  "lookback_requested_sessions": 500,
  "lookback_eligible_sessions": null,
  "input_manifest_hash": null,
  "algorithm_version": "research/0",
  "features": {
    "sma_10": null,
    "sma_30": null,
    "sma_200": null,
    "distance_to_sma_200_pct": null,
    "distance_atr_units": null,
    "distance_rank_percentile": null,
    "rank_prior_sample_size": null,
    "persistence_sessions": null,
    "approach_velocity_pp_per_session": null
  },
  "context_ref": null,
  "traversal_event_ref": null,
  "analogue_outcome_ref": null,
  "status": "uncomputed"
}
```
This is *not* a B00-approved schema. The identifiers and algorithm versions are placeholders, not materialized records.

## Reuse/discrimination rule
Admit a feature to an approved interface only if (a) it is nonduplicative or has a documented semantic distinction, (b) survives point-in-time replay and data-quality tests, and (c) demonstrates incremental explanatory value over existing simpler baselines on held-out periods. If only interpretable and not incrementally discriminatory, retain as optional explanatory metadata, not a trading feature. No quantitative probabilities, regime forecasting or fair-value inference until B07 separately validates.

## Experimental precision policy for B00 review (2026-11-04; not approved shared schema)

These rules resolve ambiguous research calculations before implementation. **They are candidates for B00 #103 approval, not authority to change a shared engine or data writer.**

| Feature | Predeclared research definition and edge behavior |
|---|---|
| Session index | Sort distinct, verified **completed exchange-local sessions** strictly by session date. Adjacent indices are adjacent eligible trading sessions, not successive 24-hour periods; reject duplicates and conflicted corrections. |
| SMA_N | Sum of the most recent N valid, homogeneous adjusted completed closes divided by N. `SMA_N(t)` includes session t only when bar was available by decision `as_of`. For an intraday decision, latest eligible is the previous completed session. Null before N. |
| SMA slope over k=5 | `100*(SMA_N(t)/SMA_N(t-5)-1)` in **percent**, not percentage points; requires `N+5` eligible sessions. Null on missing baseline or nonpositive denominator. |
| Price distance | `100*(close/SMA_N-1)` in percent; changes between distances expressed in **percentage points**. `approach_velocity = (distance_pct(t)-distance_pct(t-5))/5` in pp/completed session. |
| ATR14 Wilder | True range `TR_t=max(high-low, abs(high-previous_close), abs(low-previous_close))`; initial ATR at the 15th eligible bar equals the arithmetic mean of TR for bars 2–15, then `ATR_t=(13*ATR_(t-1)+TR_t)/14`. Null until 15 valid consecutive eligible bars and on unresolved source gaps. `(close-SMA_N)/ATR14` is measured in ATR units and null when ATR <= 0. |
| Consecutive persistence | Signed count of consecutive completed sessions satisfying close > SMA_N (+) or close < SMA_N (−) through t, ending at first equality, gap or invalid state; equality produces 0. If run extends beyond available prehistory, report `left_censored=true` rather than treating truncated count as a proven full duration. Use **consecutive** count, not PAIRED_REPLAY's separate 10-session signed occupancy fixture. |
| Historical percentile | For a 200D distance, primary full-sample experiment uses **exactly 252 strictly prior eligible distance values**, midrank `100*(#prior < current + 0.5 * #prior == current)/252`, from as-of-eligible data; null with reason if <252. With 200D warmup this requires >=452 completed daily bars. A variable-n shorter-lookback rank may be exposed as separate provisional descriptive metadata with explicit n, never substituted in the primary comparison. |
| Return outcome | For event t, `100*(close_(t+h)/close_t-1)` using h completed future sessions, available **only in retrospective resolution** and never in observation-time features. Missing future horizon -> censored, not 0. |
| Episode and clock | #145 owns frozen event boundaries, onset, tie/ambiguous bar ordering and outcome clock. The same episode ID and observation-time cohort must be used for baseline and +slope; one episode is one independent evaluation unit. |

### Newly authoritative storage constraint — B00 handoff #183

Every newly written **physical JSONL** must represent exactly one exchange/session date per instrument and data kind. B00 decides actual paths and versioned cutover; B02 writer owns atomic date validation and late corrections in their original session partition, preserving immutable legacy source histories. B06 is a **read-only consumer** of an approved indexed partition resolver, not a JSONL writer. The daily-state calculator must **not** assume that one legacy multi-day `history.jsonl` remains the canonical long-history input or try to create it in B06. As-of join and rolling windows operate across approved session partitions returned by the reader. See [#183](https://github.com/whiterosecoffee/_BASKET/issues/183), [#148](https://github.com/whiterosecoffee/_BASKET/issues/148).

### First registered research comparison

**Only** B06 #109/#145 traversal baseline vs *identical* baseline plus `SMA30_slope_5` calculated from the last fully available completed daily session. Training, eligibility, frozen episodes/labels, event clock, cohort, split and total alert count must be identical; report denominator, episode clusters, uncertainty and missingness. Do not retrospectively select a different comparison based on the NVDA November 4 example. Slope promotion is contingent on held-out gain; null/negative result retains the simpler baseline.

### Conformance fixture IDs to request (not execution claims)

`SMA-N-9-10`, `SMA-N-29-30`, `SLOPE-30-34-35`, `SMA-N-199-200`, `SLOPE-200-204-205`, `RANK-200-451-452`, `ATR-14-14-15`, `ATR-ZERO`, `PERSIST-TIE`, `PERSIST-LEFT-CENSOR`, `PIT-INTRADAY-FINAL-CLOSE`, `SESSION-DST-EARLY-CLOSE`, `PARTITION-MIXED-DATE-REJECT`. These are proposed golden tests for the appropriate owners B06/B02/B01; they are **not** reported as passed.
