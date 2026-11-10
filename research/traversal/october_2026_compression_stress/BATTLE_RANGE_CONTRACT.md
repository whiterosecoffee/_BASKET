# Battle ranges and append-only traversal event ledger — research contract v0.1

Status: proposed B06 research contract, not registered shared schema or deployed implementation. Issue #144 / draft PR #145. This document extends October 2026 stress-test methodology without touching active B06 engine or B00 schemas.

## Core principle

A **battle range** is a persistently identified, time-bounded or open-ended price interval with a frozen discovery-time boundary and explicit parent/overlapping range relationships. A **traversal event** is a point-in-time observation/change pertaining to a range; later outcomes are appended and refer to earlier evidence by immutable IDs, never rewrite prior states. A **comparison** is a derived versioned view of multiple ranges/events and defined clocks, not a mutable historical label.

### Data layers (three separable contracts)

1. **Range definition snapshot**: `battle_range_id`, ticker, venue, currency, discovery timestamp, low/high, boundary method, discovery_bar_hash, parent_id(s), overlaps, source period/session, creation model/config version. Bounds frozen at discovery. New revisions/new IDs when boundaries evolve; never silently recenter after outcome.
2. **Append-only event ledger**: immutable ID, range_id, event type, event_at, observed_at, available_at, ingested_at, as_of, source class/provider/entitlement, quality/TTD, input hash, measured price/turnover/path efficiency, candidate or confirmed designation, causation refs. Out-of-order corrections use supersedes/retracts events; stable deterministic dedupe IDs.
3. **Derived comparisons**: algorithm+git/config+input hashes, as-of clock, historically available comparator cohort, nested range position, dollar- and volatility-normalized impact, status and unresolved missing inputs.

A range may cross sessions, be nested, adjacent or overlap multiple parents. Do not force a single parent if overlapping ranges explain differing time-scales. Time scale is metadata: 1m / 5m / 15m / 30m / session / multi-session / 20d / 200d are views over one underlying immutable observation stream, not independent reconstructed truth.

## Event vocabulary

`range_created`, `boundary_contact`, `downward_expansion`, `absorption_candidate`, `stabilization_attempt`, `rebound`, `rejection`, `boundary_breach`, `failed_stabilization`, `higher_low`, `reversal_candidate`, `reversal_confirmed`, `continuation`, `range_expired`, `correction`.

`failed_stabilization` refers to a prior candidate and is observable only on completed breach. A candidate may still be unresolved when its fixed horizon ends. `reversal_confirmed` must use structural conditions frozen before observation; if directional flow unentitled, represent reduced-confidence price-only confirmation (not signed-flow proof).

## Measurement vector (per completed window, per range)

- `return_bp = 10000*ln(end/start)`, `velocity_bp_per_min`, `acceleration_bp_per_min2` (only after clock alignment)
- `notional_usd = Σ minute VWAP*shares`, `notional_usd_per_min`, same-clock relative turnover vs 20 prior eligible sessions (fail closed with insufficient history)
- `impact_bp_per_usd_b = return_bp/(notional_usd/1e9)`; paired with `abs_impact`, never interpret this as causal impact or net capital flow; estimate Kyle lambda only when signed trade pressure is available and assumptions are documented
- `path_efficiency = |Σ log(close_t/close_(t-1))|/Σ|log(close_t/close_(t-1))|`; record realized path length and high/low separately
- `range_position = (price-low)/(high-low)`; outside-range values allowed and meaningful; range zero width => null
- `boundary_contacts`, `boundary_break_distance_bp`, `contact_duration`, `next_low_time`, `attempt_sequence` and `impact_decay_since_first_contact`
- `ATR_or_realized_vol_scaled_velocity`, `peer_residual` vs predeclared QQQ/SMH and market factors; no dynamic hindsight peer choice
- `flow_imbalance` null unless entitled trade+quote observations support defensible aggressor-sign assignment
- `auction_flag`, `bar_completeness`, `data_delay`, `TTD_status`, split adjustment policy and market calendar ID

**Cross-window relativity**: compare same-clock, same-horizon, same volatility regime baselines; show both absolute impact and percentile/z within the ticker's prior eligible windows; never compare a $1B QQQ turnover window mechanically against a $1B microcap window. Aggregate bottom-up with non-overlapping windows; don't sum nested range turnover (double counting).

## Example event JSONL (synthetic example, not November 2 observation)

```jsonl
{"event_id":"evt-001","type":"range_created","range_id":"QQQ-202610-example-A","ticker":"QQQ","at":"2026-10-16T18:00:00Z","low":710.0,"high":715.0,"parent_ids":["QQQ-example-session"],"model":"battle.v0.1","source_class":"synthetic_fixture"}
{"event_id":"evt-002","type":"stabilization_attempt","range_id":"QQQ-202610-example-A","at":"2026-10-16T18:15:00Z","defended_low":710.0,"notional_usd":800000000,"reference_id":"evt-001","model":"battle.v0.1","source_class":"synthetic_fixture"}
{"event_id":"evt-003","type":"failed_stabilization","range_id":"QQQ-202610-example-A","at":"2026-10-16T18:30:00Z","price":709.9,"breached_low":710.0,"reference_id":"evt-002","model":"battle.v0.1","source_class":"synthetic_fixture"}
```

Production event records require full temporal, provenance and hash fields; examples intentionally use a reduced explanatory shape and **must not** be ingested into canonical history.

## Critical safeguards

- Candidate and realized outcomes stored separately. No retrospective rewriting, future-dependent boundaries, or winner-selected events.
- Nesting does not permit double counting; range-level aggregates refer to underlying bar IDs with single-count windows.
- A new low on reduced impact is *not* automatically absorption. Bid/ask trade-sign unknown on OHLCV.
- Gap, intrabar ordering, contradictory prints, trade correction, split/ETF distribution, closing auction must be explicit.
- Provenance supports deterministic replay with exactly identical event IDs from the same immutable input snapshot.
- Multi-horizon forecasts/probabilities disabled unless calibrated and independently validated by B07 and B01.

## Tests proposed to receiving implementation

1. Freeze range bounds and only append state transitions; show no hindsight mutation after failed bounce.
2. October 16 QQQ/SMH low-close continuation vs October 30 earlier low and recovery; classify full sequence, not closing label alone.
3. Failed stabilization within a higher-timeframe trend vs true local reversal nested in broader downtrend.
4. Wide spread / zero volume / trading halt / 15m missing bars / auction artifact / outside-range contact / duplicate and corrected bars.
5. Cross-instrument same-clock turnover/impact baselines and index-vs-components correlation; avoid parent-child double counting.
6. Full universe October replay including controls and failures, threshold sweep, purged walk-forward and November 2 locked holdout.
7. Explicit false positive, late alert, missed rebound, horizon censoring and transaction cost reporting.

## Prior art mapped to components

- Volume profile / market profile: density zones, but minute VWAP bins approximate exact volume-at-price.
- Market microstructure, Kyle (1985), Amihud (2002): price response vs traded activity; causal impact requires signed order flow.
- Change-point detection / CUSUM / volatility estimators: adaptive window and regime transitions with lookahead-controlled thresholds.
- Event sourcing / bitemporal data / CQRS: immutable events, corrections, derived projections; as-of replay.
- Interval graphs / multi-resolution time series: overlapping and nested battle ranges without forced single-parent trees.
- Survival analysis: time-to-breach / time-to-confirmation with censored unresolved attempts; only fit probabilities after sufficient validation.

Integration owner: B06 traversal; B02 market feed/history; B00 registered schema; B01 integration tests; B07 calibration. No direct edits outside research/traversal/** in this branch.
