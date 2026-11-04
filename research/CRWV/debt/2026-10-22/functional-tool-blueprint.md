# CRWV functional analysis tool — conversation synthesis and implementation specification
Date: 2026-10-26. USD. Status: proposed domain component; not an operational service.
Source workstream: B10 #68, draft PR #69. This specification is within the existing research-only write scope. It grants no shared-engine or runtime ownership.

## Outcome
One reproducible company model should answer: What changed? How much capacity is actually earning? Can the next deployments be funded? What cash/earnings reach a diluted share? What is today's price assuming? Is CRWV moving differently from its sector? Where are statistically supported traversal zones?
Produce structured data and a concise rendered view from the same calculations. Research prose is supporting evidence, not the calculation engine.

## Existing work and limitations
- debt-stack.json / debt-repricing-2026-10-23.json: dated instrument evidence, commitments, subsequent events, current maturities and repricing mechanisms. Not a current reconciled balance.
- capacity-conversion.md and integrated-assessment.md: sourced operating milestones, recognition windows, NVIDIA support, competition and pricing. No complete customer/site acceptance ledger.
- factor_tracker.py and factor-closes-2026-10-23.csv: executable prior-60-return OLS attribution for CRWV vs QQQ/NVDA and HYG/IEF/USO. No live ingestion. Same-day factor use makes this ex-post attribution, not a next-session forecast.
- october-turnover-velocity.json: dated raw daily inputs and descriptive turnover/velocity. Gross trades cannot identify unique owners or net capital flows.
- capacity-scenarios.py/json: executable illustrative scenario, not a facility-based credit model. Assumes $50B starting debt, $3B cash, 600M shares, $9B annual legacy depreciation, uniform scenario debt rate and automatic equity funding. These are assumptions, not verified current balances. Automatic funding masks an infeasible funding plan.
- forward-valuation.md and capacity-weighted-valuation.md use different assumptions. A 26% GAAP-like modeled margin is not equivalent to management's adjusted margin target. Targets must be regenerated from one versioned parameter set, not blended across models.
- #70 is an open requested ingestion/traversal handoff. No continuously refreshing tracker is deployed. PR #69 remains unmerged as reviewed this turn. Latest-head CI is not independently verified in this review.

## Components and measurements
| Component | Required inputs | Output / decision |
|---|---|---|
| Evidence and time | dated filings, contracts, market data, source revisions, statement class | source coverage, conflicts, historical/expired/current state, replayable input snapshot |
| Capacity and fulfillment | site/cluster/cohort IDs, gross and IT MW, energized/installed/accepted/billable dates, equipment generation | billable MW-months, quarterly additions, utilization, delivery lag, delayed-cohort revenue |
| Contracts and realized pricing | customer/order IDs, term, minimum payment, prepay/refund terms, start/expiry, GPU/service mix | revenue/MW and GPU-hour by cohort, scheduled backlog recognition, repricing exposure, margin by vintage |
| Debt and liquidity | instrument/facility IDs, commitment/drawn/eligible availability, coupon/spread/benchmark, hedge, fees, amortization, security/covenants | monthly cash waterfall, debt service, headroom, unhedged sensitivity, refinancing needs, earliest funding gap |
| Earnings and cash | direct operations, rent/power, D&A, corporate costs/SBC, cash/expensed/capitalized interest, tax, capex and principal | GAAP-like and adjusted earnings reconciliations, operating cash, sustaining/growth cash uses, attributable free cash |
| Equipment lifecycle | deployment age, remaining book value, expected earning life, renewal pricing, maintenance/failures, power efficiency, resale/trade-in terms | economic residual value, accounting D&A sensitivity, incremental cash from years 7–9, replacement decision |
| Capitalization and valuation | equity/convertible terms, share classes, SBC, issue prices, forecast cash flows, discount rates/multiples | EPS, enterprise/equity bridge, dilution, present fair-value scenarios, 3/6/12/24-month targets, reverse valuation |
| Market and credit attribution | synchronized CRWV/QQQ/NVDA returns, HYG/IEF/USO, issuer yields/spreads and benchmarks | conditional factor returns, residual divergence, rolling stability, macro-vs-issuer evidence |
| Traversal and turnover | entitled daily/minute OHLCV, session, bid/ask or trades if available, float/date | anchored VWAP, dollar turnover, return per notional, price-bin density, revisit/transition rates and execution-adjusted cycle measures |
| Competition and demand | delivered/unallocated/booked capacity, same-generation quotes, contract tenor, workload benchmarks | relative delivered cost, pricing premium, cost per useful task, supply bottlenecks and substitution |
| Thesis and valuation history | observations, assumption versions, scenarios, subsequent actuals | what changed, valuation bridge, forecast error, falsification, unresolved assumptions |

### Important distinctions from the conversation
- Contracted power, active power, billable IT power and facility power are distinct.
- Backlog/RPO/current revenue/exit annualized revenue are distinct. Deliveries starting on a contract do not recognize its whole value.
- $40M/MW short contracts cannot price every long-duration fleet cohort.
- NVIDIA residual-capacity purchasing applies to covered arrangements subject to delivery/availability; never assume 100% protected utilization across every future MW.
- Favorable secured financing is not a uniform corporate funding cost or proof the whole pipeline is funded.
- Fixed coupon does not reset with traded yield. Floating benchmark can reset without refinancing. New financing after a fixed-price customer contract can create exposure.
- Capex is capitalized, not a full current EPS expense. Principal reduces cash, not earnings. Depreciation and a second full replacement expense must not both be charged to the same earnings construct.
- Accounting useful-life extensions do not create cash or automatically mark assets up to fair value. Economic life/resale value may increase DCF value independently. A100 architecture age is not each physical unit's age.
- NVIDIA trade-in/residual guarantees remain a research question unless verified for the exact beneficiary, equipment, term and conditions. Do not transfer another project's guarantee to CRWV.
- Higher demand does not mechanically imply better corporate credit; cash coverage and leverage must improve.
- Price declines are not themselves multiple compression; synchronized forward earnings are needed. Factor residual is not proven mispricing or company news.
- Volume/float is turnover, not percentage of unique holders replaced. VWAP is traded-price average, not remaining holders' cost basis.
- Low volume/large price moves are descriptive without signed flow/order book; distinguish thin bids from seller exhaustion. Do not mechanically extrapolate equal buying into equal upside.
- Slow/base/bull weights are explicit assumptions until calibrated. Never present subjective weight as measured market probability.

## Proposed interface (not yet implemented)
Pure domain entry point: evaluate(snapshot, scenario_config, as_of, horizons) -> analysis_result.
Read local approved upstream data; never fetch live APIs inside valuation functions.
Snapshot references and assumption values are versioned and content-hashed.
Local domain contracts under research/CRWV/tool/contracts/ are proposed; shared schemas require B00.
Proposed input groups: evidence, capacity_cohorts, contracts, facilities, hedges, assets, operating_costs, capitalization, market_observations, competitors, scenario_config.
Proposed result groups: freshness, coverage, operating_forecast, funding_waterfall, earnings_bridge, lifecycle_sensitivity, dilution, valuation_curve, reverse_valuation, attribution, traversal, changes_since_prior, unknowns.
Each derived metric carries units, period, data status, dependencies, source IDs and method/config version.
Represent required-missing values as null with a reason; do not silently impute zero.
Exclude information first available after as_of. Store effective_at/period_end, available_at, observed_at, ingested_at, expires_at and revision identity separately. Unknown publication time remains unknown.
Permit partial output for unaffected components; block only dependent conclusions. Historical replay can be valid while data is stale for a current claim.

## Economic calculations
Monthly forecasts for at least 36 months; annual/cohort tails extend far enough to test economic life, not just 2028.
Revenue is built from billable exposure and service pricing, constrained/reconciled to contract schedules; newly signed deals and services are separate from a fixed old RPO pool.
Debt is modeled by instrument with scheduled balances, benchmarks, hedges and draw conditions. Parent and restricted project cash are distinct.
Liquidity must allow a funding_gap state. Equity/debt cannot appear as free automatic balancing items. Financing is an explicit approved scenario with cost, availability, limits and share impact. A delay response must defer both relevant spending and earning dates.
Maintain separate accounting earnings, cash flows and economic value. Use after-interest net-income/P-E without subtracting debt again, or enterprise DCF with a consistent net-debt/lease bridge.
Depreciation-life changes are prospective estimates on remaining depreciable balances; no reversal of accumulated depreciation. A hypothetical full-life illustration is not a forecast of the actual in-service fleet.
For trade-in economics compare keeping old equipment's remaining discounted earnings/resale with upgrading: net invoice after conditional credit, financing, installation downtime, useful throughput and power opportunity cost. Do not collect both retained old-fleet earnings and surrendered-asset credits in the same branch.

## Valuation through time
Store separate valuation_as_of, financial_forecast_period and target_date.
Show present fair value and future-date conditional value separately. The valuation curve is not a stock-price-path prediction.
At each revision preserve:
1. the original forecast and then-known evidence;
2. actual realized observations;
3. a comparable fixed-horizon valuation bridge separating capacity/delivery, price/mix, operating margin, life/residual, funding/interest, dilution, discount/multiple and time roll;
4. any reconciliation interaction, with decomposition order/method declared.
Compare scenarios at the same horizon and share-count convention. Use appropriate valuation methods when EPS is negative.
Reverse valuation solves required billable capacity, revenue/MW, operating margin, net interest and dilution at a given quote; the observed price does not uniquely determine these assumptions.
Weights must sum to one when used, remain labeled subjective/empirical, and permit no-weight sensitivity output. Backtest probabilistic forecasts before calling them calibrated.

## Traversal implementation requirements
Use 5/20/60-session windows plus Oct7 anchor with year/exchange session explicit. Keep premarket, regular and after-hours separate.
Dollar turnover = sum(trade price * shares), or labeled bar-VWAP approximation. Anchored VWAP = total notional / total volume.
Report signed net return/notional and gross traveled range separately; normalize by volatility and comparable time-of-day participation.
Touch events need fixed band width, minimum separation/hysteresis and clear first-passage rules; minute OHLC cannot establish within-bar ordering or precise volume-at-price. Do not create repeated-touch counts from neighboring bars without debouncing.
Report denominators, sample size, censoring, regime and uncertainty for transition rates. Validate with walk-forward held-out data, spread/slippage/fees and missed rebounds. No promised cycling profit.
Factors train only before the explained observation. QQQ/NVDA fitted jointly; HYG/IEF/USO are proxies, not direct issuer spreads/SOFR/spot oil. Actual issuer credit changes require own observations.
Do not add correlated component effects from separately fitted regressions.

## First executable milestone
Build a local snapshot -> capacity revenue -> instrument cash waterfall -> earnings/dilution -> valuation -> JSON/text result path using dated fixtures.
It must show funded and unfunded scenarios explicitly, an acceptance delay, fixed-coupon invariance to traded-yield shocks, floating benchmark exposure and asymmetric depreciation-versus-cash changes.
Existing research data is read-only evidence; audit/transform the minimum inputs, preserve source SHA, avoid wholesale duplication.
Integrate existing factor/traversal outputs through adapters after the core finance path works. Do not create a standalone website first.
Domain tests must cover arithmetic conservation, units, date cuts, no-lookahead, conditional funding, anti-double-counting, dilution and residual/trade-in exclusivity.
Document exact command, generated output and limitations. Shared owner integration and actual persistent execution are later gates, not blockers to an offline component.

## Ownership and launch
New conversation suggested title: CRWV — Operating Economics & Valuation Tool.
New worker must read current main AGENTS/catalog/protocol and open issues/PR file scopes, create its own issue and unique current-main-based branch.
Proposed disjoint writes: research/CRWV/tool/**, only after collision check. Existing #68 owns research/CRWV/debt/2026-10-22/** and remains read-only to the new worker.
B02: canonical market ingestion; B03: filings/events; B04: shared valuation; B05: relationships; B06: traversal; B07: calibration; B08: runtime/presentation; B00: shared contracts/routing; B01: CI.
Reuse #70 for existing feed/traversal dependency rather than opening a duplicate. Register new dependencies only when actually needed.
This spec does not launch a new conversation, allocate dormant branches or certify operational readiness.
