# Floating Relative Value Rotation Index
Version: proposal0.2. ID: FLOATING_RELATIVE_VALUE_ROTATION. Status: formal contract; no live controller, execution, automated monitoring or validated trading advantage.
Parent: feature-design-rotation.md. Compose existing B04 engines/valuation/rotation at PR298; current source pin56e9e03693cfcd71cf0ca04d50470332110defda. B15 owns this consumer specification; B04 owns shared implementation. Origin #305, receiver request #311. SNDK/SKHY is the first instance, not a new valuation engine.

## Purpose and corrections
Compare how many shares and how much future recurring earnings a holding can purchase in another established company as executable prices fluctuate. Support switching in either direction when relative opportunity clears explicit costs and uncertainty. Do not schedule a calendar rotation or assume a report creates a price jump.
Prior 2027 exchange-ratio peak and very low terminal P/Es are illustrative assumptions, not timing instructions or default fair values. Price and EPS paths are uncertain. Relative multiples must be justified under consistent market conditions, with sensitivity; identical P/Es are a diagnostic only. Do not hardwire the previous3–4.5x values.

## Composition
- Parent capability: constrained relative allocation, referencing the prior design.
- Independent modules: source/freshness gate; common-date valuation adapter; directed ratio/index calculator; private account/cost ledger; stateful band policy; path/replay evaluator.
- Instance: SNDK→SKHY and SKHY→SNDK, USD, correct split and ADR units.
- Multi-ticker generalization: compute price/value discount for each instrument and directed pair indices; preserve holding/cash alternatives. No custom forecast or ingestion per pair.

## Inputs
Use inherited source manifest and temporal fields. Supply matched bid/ask/depth/session, endpoint-specific recurring diluted EPS, reconciled earnings basis, justified relative valuation ranges, expected distributions, original currency/date-matched FX and instrument basis. Keep pre-split vs post-split and Korean common vs USD ADR distinct.
Account inputs stay private: lots, taxes/cash timing, available shares, spreads/slippage/fees/ADR charges, financing, minimum cash/equity, broker/session/settlement constraints, group concentration.
For each earnings announcement checkpoint, record confirmed or estimated date separately from fiscal period_end and forward EPS window. Quarterly rolling next12months estimates must be sourced/reconciled; annual EPS is not silently relabeled NTM. No fabricated quarterly interpolation or exact report dates.
Maintain both fixed calendar endpoint comparisons and rolling horizons as separate views; horizon roll and EPS revision are separately attributed. No aggregation across horizons without declared preference/weights.

## Math
For A=SNDK, B=SKHY, scenario s and matching endpoint T:
V_A=forward EPS_A(T)*justified multiple_A(T); likewise B, or declared alternative valuation for loss-making firms.
Fair exchange ratio F_AB=V_A/V_B.
Observed executable purchasing power R_AB=bid_A/ask_B.
Directed index I_AB=100*R_AB/F_AB.
Interpretation:100 is modeled gross terminal-wealth parity. Above100 favors A→B under that scenario; below100 favors retaining A. Reverse executable index is calculated separately from bid_B/ask_A and V_B/V_A; it is not exactly10000/I_AB because spreads are directional.
Reference/midpoint visualization may be reciprocal but must be labeled non-executable.
Candidate future earnings purchased per A share = R_AB*EPS_B(T); retained A earnings=EPS_A(T). This is attributable corporate earnings, NOT dividends/cash available for spending and NOT an investment decision independent of multiple, capital needs and risk.
For actual lot sizes use existing discrete ledger extended to count residual cash, taxes and financing exactly once. Prefer index-equivalent net wealth ratio derived from the ledger; do not subtract a random number of score points for taxes.

## Policy state
State includes held quantities, last fills/time, input versions, per-direction thresholds, revalidation time and unknown gates.
Actions: hold / partial A→B / full A→B / partial B→A / full B→A / retain cash; execution remains manual.
Illustrative cost-free10% relative wealth hurdle:
- A→B requires I_AB>=110.
- B→A requires its separately calculated I_BA>=110. In frictionless reciprocal display this corresponds to I_AB<=90.909.
- Between bands: hold. This hysteresis avoids an immediate reversal at parity; exact bands require uncertainty, costs and replay calibration.110/90.909 are examples, not validated parameters.
Recompute F and bands after justified forecast/multiple/FX revisions; reevaluate eligibility after any invalidation. Keep a frozen-baseline index alongside the current fair-value index so model revisions cannot masquerade as price outperformance.
A margin/illiquidity/invalid-input veto supersedes score. Position caps apply at portfolio/group level. Only label robust when all required scenarios clear the net hurdle; otherwise scenario-dependent/unknown. No invented probability.

## Two-way share accumulation example
Purely synthetic:100A exchange at1B perA gives100B; later B costs0.8B perA, so100B buys125A. Gross share count gain25%. With per-conversion retained-capital factors k1,k2, final A=N*R_entry/R_exit*k1*k2 (fractional, no taxes/dividends). Use actual directed bid/ask and ledger in implementation. A decline in A's fair value may make its lower ratio justified: never trade a raw ratio without updated fundamentals.
This example proves arithmetic only, not repeatability, rising account wealth or market predictability.

## Output contract
As-of matrix per horizon/scenario: A,B,executable ratio, modeled fair-ratio range, directed index range, net hurdle, threshold prices, shares/cash after action, forward earnings purchased, held earnings forgone, downside/margin effects, current action state, exclusions and source/forecast revisions.
Display dates as report_date (confirmed/estimated), period_end, forward EPS window and valuation date separately.
Explain movement by price, EPS revision, relative multiple, FX, horizon roll or cost/account change. Missing data must suppress affected recommendation rather than silently inherit a stale value.

## Checkout/review acceptance
1. Exact published packet reachable in receiving Spark session; record host/session, source checkout preservation, destination repository/branch/SHA/path, scoped owner and acknowledgment. No receipt can establish this from sender alone.
2. Reuse B04 #297/PR298 and #198 forecasts; do not create duplicate stores/models. Resolve live ownership before implementation; this checkout assignment is read-only source review plus offline replay and review artifacts.
3. Reproduce parent synthetic CLI and distinguish its ignored residual cash/tax/financing limitations. Evaluate index parity, directed spread, identical-ratio rising prices, estimate revisions, horizon roll, stale quotes, cost drag, reverse-band behavior and round-trip example. Run meaningful existing checks; no large mirror-test suite.
4. Reject NaN/infinite/stale/lookahead/mixed basis, unverified account feasibility and unsupported report dates. No current signal using historical summaries.
5. Produce a gap assessment and smallest B04 implementation increment; record actual command/output and exact source revisions. No merge, trading, schedules or claims of live operation.

## _PATTERNS methods
Canonical lookup: read current default-branch AGENTS.md, Snapshot.json and Handoff.md. Resolve _AGENT_FRAMEWORK and _WORKSTATION_HANDOFF through receipt component rows, verifying IDs and exact state/guidance revisions. Do not presume latest branch tip equals published component.
Verified method pins read for this packet:
- _AGENT_FRAMEWORK0758c08f1a8c5451a07df652bfaba985c7f6670b, _LIBRARIES/_MICROSOFT/_AGENT_FRAMEWORK/{AGENTS.md,state.json,ADOPTION_REVIEW.md}.
- Reviewed checkout skill9b915dcf5f644ca492ae7a3b900c5644025a4d8c, same home/skills/review-prepared-checkout/SKILL.md.
- Prepared transition131830964900dad0d52d6f716643b0cac318d2c1, _PROMPTS/_HANDOFF/COMPLETE_PREPARED_CHECKOUT.md.
- _WORKSTATION_HANDOFF59b4a88638293a0c2a5dba12afee269fdd33f934, _TOOLS/_WORKSTATION_HANDOFF/{AGENTS.md,state.json}.
These are reusable guidance/offline checks, not authority for remote actions or mandatory Microsoft runtime installation. Typed synthetic fixture is not evidence of live pickup.
