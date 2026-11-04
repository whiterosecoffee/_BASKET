# B06 market_watch_gate — offline qualification only

This is the smallest independent maturation increment in B06 #155/PR #182. Pure Python, no provider calls, storage, scheduler or notification transport. It deliberately **does not** compute the underlying market regime, high/low, order flow, confidence or a price forecast. Those remain with B06 market geometry and future externally verified detector, B17 market context and B07 calibration.

## API
```python
from gate import qualify
decision = qualify(event, prior_event_id="prior-episode-id-or-null",
                   cutoff="2026-11-04T16:00:00Z", max_lag_seconds=90)
# {"schema":"basket.market_watch_gate@1","notify":false,
#  "event_id":"...","reason_codes":["duplicate_event"]}
```

The caller must supply **confirmed**, **material**, source-verified input and non-conflicting pricing; event_at, available_at, cutoff with UTC offsets; evidence IDs; a versioned stable event_id; a known session; and the most recent durable event ID (if known). For cross-asset alerts, the caller must explicitly set `requires_cross_asset=true` and `cross_asset_synchronized=true` only when verified against the same cutoff. The gate refuses stale, unconfirmed, duplicate, unknown or conflicting inputs.

For after-hours, `material_after_hours=true` is mandatory even if the provider reports a generally open market; other sessions require `market_open=true`. The gate uses the **caller-supplied lag policy**, it does not invent a market-event threshold or compare economic materiality. `notify=true` means only that the provided evidence meets this gate, **not** that a notification was delivered or market confirmation independently verified.

## Constraints and dependencies
- Previous event_id must come from B02/B08-qualified durable state. This component does not persist it, so repeated calls without prior state may repeat decisions.
- Timestamp/entitlement/source validity asserted by caller, not checked against Massive inside this code. A true `source_verified` flag alone is not a provenance certificate.
- A separate versioned regime detector is required to supply market episodes and calibrated confirmation/hysteresis thresholds; do not substitute this gate for it.
- B00 owns shared schema and session contract; B02 owns daily partition files #183, history/replay; B01 independent cross-domain integration; B08 delivery.
- No claims of historical alert precision, volume-based floor, real-time data feed or cross-asset index attribution.

## Local synthetic validation
```sh
python -m unittest discover -s engines/traversal/market_watch_gate -p 'test_*.py' -v
```
Author-local Python 3 execution on 2026-11-04: **15 tests passed**, zero skips/errors. No repository-hosted exact-head CI is claimed. Tests cover positive qualification, duplicate, stale, future/naive timestamps, no evidence, invalid TTL, unconfirmed/immaterial, quote conflict, missing synchronized cross-market, regular closed market, material and immaterial after-hours and invalid event type. The cutoff/fixtures are synthetic; actual Massive source/session data and B01 CI remain pending.

Full dependency-ordered scoring and roadmap: `research/traversal/market_flow_watch_review/BROAD_MATURATION_PLAN.md`.
