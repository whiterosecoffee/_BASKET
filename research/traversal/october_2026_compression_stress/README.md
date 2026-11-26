# B06 #144 — Historical Battle-Range Recognition

**Status:** Research specification and dated observations; **not** a validated detector, strategy, live service, or deployed ingestion path.  
**Owner:** B06, issue [#144](https://github.com/whiterosecoffee/_BASKET/issues/144), branch `work/144-october-compression-stress`, draft [PR #145](https://github.com/whiterosecoffee/_BASKET/pull/145).  
**Exclusive write scope:** `research/traversal/october_2026_compression_stress/**`. No changes to `engines/traversal/**`, `_TICKERS/**`, `tickers/**`, `runtime/**`, `schemas/**`, shared tests or other active worker paths.

## Decision and scope, November 3, 2026
- **Primary goal: recognize historical market behavior.** Classify the local sequence: range created → contested boundary → candidate absorption / stabilization → hold, breach, failure, continuation or confirmed local reversal. No entry optimizer or probability score in #144.
- **First acceptance evidence: historical falsification.** Use completed October 2026 RTH sessions and November 2 as a diagnostic replay, including all qualifying cases and counterexamples; do not cherry-pick successful events. November 3 is subsequent illustrative as-of replay, not an automatically valid out-of-sample test because parameters were discussed after watching the session.
- **One canonical source.** Read ticker data via the B00-approved `resolve(instrument_id, data_kind, access_mode, as_of)` targeting logical `_TICKERS/{ticker-symbol}`. B00 [#148](https://github.com/whiterosecoffee/_BASKET/issues/148) migration is pending. Never copy raw observations into B06, implement a second data store or silently bypass the resolver. When resolver is unavailable, return `BLOCKED_CANONICAL_DATA` with a source-coverage request for B00/B02; no synthetic fill.
- **Reuse existing work**: B06 [#108/PR109](https://github.com/whiterosecoffee/_BASKET/pull/109) canonical range engine, B06 [#149/PR150](https://github.com/whiterosecoffee/_BASKET/pull/150) synchronized market geometry, [#154](https://github.com/whiterosecoffee/_BASKET/issues/154) moving average discrimination, B10 [PR99](https://github.com/whiterosecoffee/_BASKET/pull/99) source-event journal and B17 [PR101](https://github.com/whiterosecoffee/_BASKET/pull/101) market context. No competing new engine or poller here.

## One minimal functional recognition unit

**Input:** A time-ordered, complete-bar view returned by the authorized resolver, with instrument ID, venue/session/calendar, bar identity, original and adjusted price policy, UTC `effective_at`, `available_at`, `ingested_at`, provider, quality/TTD, source manifest hash, fixed lookback/config, optional prior `battle_range_id`.

**Output:** An experimental `battle_transition@0.1` *derived* event or `unresolved` with:
- immutable `event_id`, `range_id`, `parent_range_ids`, `input_ids/hash`, `as_of`, `model_version`, `config_hash`;
- frozen discovery-time `low/high` and a reference to the last defended boundary;
- `state_from`, `state_to`, `trigger_bar_id`, `observation_time`, `available_at`, `status` (`candidate|confirmed|unresolved|invalidated`);
- signed return bp and velocity bp/min; dollar turnover per minute; same-clock relative turnover or null with reason; signed displacement bp/USD billion as **descriptive proxy**; gross price path and path efficiency; price position in range and boundary contacts;
- evidence class, data-quality flags, auction/gap flags and null reasons for unavailable signed order flow/depth.

**States:** `range_created`, `expansion_up/down`, `boundary_contact`, `absorption_candidate`, `stabilization_attempt`, `rejection`, `boundary_breach`, `failed_stabilization`, `continuation`, `reversal_candidate`, `reversal_confirmed`, `unresolved/expired`. A local reversal does not imply reversal of the 20-day parent. A failure becomes known only when a later completed bar breaches the *previously frozen* defended boundary. Intrabar touch/breach order is unknown from OHLCV and must not be invented.

**Comparability:** Keep separate 1/5/15/30/60/390-minute and 5/20/200-session projections from a shared canonical observation stream. Normalize velocity by volatility, turnover by ticker-and-clock reference distribution, and peer residuals against preselected QQQ/SMH/SPY/MAGS factors. Don't sum overlapping range dollar turnover or assign high activity to buyers without entitled trade/quote data.

## Acceptance (research deliverable; proofs still pending)

| ID | Acceptance check | Required proof |
|---|---|---|
| A1 | Deterministic prefix replay, no future-aware boundary adjustment, no retroactive state rewrite | Frozen synthetic transition cases plus October chronological source-ID trace |
| A2 | Failed defense distinct from true recovery, unresolved and intrabar ambiguity | Counterexamples on multiple dates/tickers, explicit timestamp of first knowable outcome |
| A3 | Correct net/gross-path, USD turnover and same-clock normalization; nulls for missing reference or signed flow | Arithmetic fixtures and independent reproducibility |
| A4 | Nested/overlapping range relationships with zero duplicate source observations | Shared input bar IDs, unique event IDs, overlap tests |
| A5 | RTH-only November 2 and subsequent November 3 replay; historical windows frozen independently of later bars | As-of manifest, exact availability, interval coverage/gaps, session/DST tests |
| A6 | Source-quality gates for fractional-volume bars, VWAP/high-low anomalies, auctions, corrections and missing timestamps | B02 [#152](https://github.com/whiterosecoffee/_BASKET/issues/152) resolved data contract or explicit blocked status |
| A7 | Quantify incremental discrimination over price-only/ATR/VWAP, under both successful and failed attempts | Event counts, confusion matrix by timeframe, delay, sensitivity, coverage and censoring; no fitted odds |
| A8 | No duplicate data, no collision with sibling B06 work and exact commit/test evidence | PR diff, source manifests, test commands/results; B01 independent CI is separate |

**Pass policy:** A written test case is not a passing test. If canonical observations or validated historical replay cannot be fetched, mark acceptance `blocked` or `not_run`. Do not report a predictor, statistically validated rank, live monitor or production schema. B07 [#93](https://github.com/whiterosecoffee/_BASKET/issues/93) owns calibration after descriptive acceptance; B01 owns cross-domain CI.

## Historical research and evidence references

The prior analysis documents **observed/illustrative** selloff behavior and does not constitute frozen-threshold validation.

- [October event examples and original hypotheses](BATTLE_RANGE_CONTRACT.md) — prior conceptual draft; this README is the controlling scoped spec.
- [Prior-art research](PRIOR_ART_SIGNAL_MODEL.md) — market profile, path efficiency, order-flow/depth, change points and event sourcing.
- [November 2 and November 3 pre-open checkpoint](NOV02_TO_NOV03_CHECKPOINT.md).
- [November 3 opening checkpoint, 09:32 ET](NOV03_OPENING_0932_ET.md).
- [Twenty-ticker backdrop at 09:38 ET](EXPANDED_BASKET_NOV03.md).
- [November 3 completed first 20 minutes](NOV03_RTH_20M_CROSS_SECTION.md).
- [Canonical data / missing-lines policy](CANONICAL_TICKER_DATA_DEPENDENCY.md) — authoritative for no-duplicate source constraints.
- [Orchestrator receiver handoff](ORCHESTRATOR_RECEIVER_PROMPT.md) — single current receiver prompt.
- [Acceptance cases](ACCEPTANCE_CASES.md) — test vectors and explicit blocker matrix.

## Next work on this branch
1. Translate the observed historical cases into input-source-ID manifests (not copied raw bars); request missing historical RTH minute intervals through B00/B02 #148/#152.
2. Execute all-candidate chronological case enumeration with price-only, turnover/path and boundary-persistence baselines; preserve negative/censored cases. Report real metrics and nulls.
3. Hand the **tested event contract** to the existing canonical B06 engine owner #108, and receive B07/B01 assessment independently. Do not start another core engine implementation.

**Time convention:** Troy, Illinois CST for human reports, ET secondary, UTC permanent. When daylight-saving offsets change, use IANA zones and session exchange calendar, not a fixed UTC offset.
