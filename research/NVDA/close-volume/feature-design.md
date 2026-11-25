# Expiry removal versus new positioning — research design v0.1.0

## Parent and composition
Use ../../../architecture/COMPONENT_QUICKSTART.md and ../../../architecture/BLACK_BOX_COMPONENT_CONTRACT.md when qualifying a public component. This research-local arithmetic helper is not a qualified component boundary. Compose with runtime/ticker_data.py (B02 data routing), engines/traversal/metrics.py (B06 descriptive measures), and engines/composites/market_context (market context). No source-store duplication.

## Problem and consumer
NVDA close/AH research must distinguish disappearing expiry exposure from fresh positioning. A small net exposure does not establish low gross exposure or low traded volume. Compare the same metric, units, source model, selected expirations and spot/IV basis before interpretation. The screenshot sequence was initially misread; preserve the user's before/after correction. Historical November4 observations are not current November19 data.

## Input/output and method
compare.py is a pure research-local function: two total-exposure observations plus the pre-removal contribution of the removed expiry. Each snapshot supplies observed_at (timezone-aware ISO), metric, unit, settings_id, universe_id, source_ref and value. Caller must verify these identities and that removed expiry is the only universe change; the helper checks declared identity, chronology and finite numbers, not source truth.

Output uses the input unit and computes:
- observed_change = after - before
- removal_only_change = -expired_before
- counterfactual_remaining = before - expired_before
- unattributed_residual = after - counterfactual_remaining

Residual is NEVER labeled new-position flow. Spot, IV, time decay, remaining-contract trades, model refresh and corrections can all change it. Even a zero residual does not prove no trades. Counterfactual is frozen-input arithmetic, not a causal attribution.

Synthetic example: before -100, expired -110, after +15 produces +10 remaining and +5 unexplained. This does not represent stock purchases. Provider-specific exposure units must be explicit; do not assign USD or shares solely from an M suffix.

## OI and price qualifications
New positioning requires matching instrument/expiry/strike/type identifiers and cleared OI vintages; delta OI is a net contract change, not investor direction or proof of a roll. Keep traded option volume, OI, gamma, delta and stock volume separate. Unknown metric or timestamp blocks qualified comparison. OI cannot be inferred from exposure deltas. Directional hedging interpretation requires verified metric and dealer-sign convention.

For close/AH comparison retain market timezone, session windows, auction/late-print conditions, adjustment basis and equal-clock historical baseline. A 15-minute closing interval versus three AH hours is descriptive, not an abnormal-volume statistic. Down-bar volume is not aggressor selling. Minute VWAP aggregates are not official session VWAP. B06 owns generic calculations.

## Prior art and limitations
Expiry-stratified counterfactual decomposition holds other inputs constant. OIC clearing semantics distinguish opening/closing trades from OI (https://www.optionseducation.org/referencelibrary/faq/general-information). MenthorQ distinguishes exposure views from OI overlays (https://menthorq.com/guide/options-menu/). References are methodological; no fresh market source was retrieved in this increment.

## Ordered advancement
1. Preserve method and validate synthetic arithmetic/invalid inputs (this increment).
2. Obtain private paired source snapshots with explicit metric/unit/model/settings and reliable times; obtain cleared OI for surviving expirations through existing B02 route.
3. Reconcile expiry arithmetic and compare matched OI keys; run on a second ticker before generalizing.
4. B00/B01 qualify an existing component boundary and independently test exact head before integration. No predictive probabilities without separate walk-forward validation.

Provider options entitlement was denied on November4; current entitlement unknown. Screenshot dates/times and selected metric were not fully verified. Public repo contains no screenshot values or raw licensed source. Source recovery/import remains separate from method completion.
