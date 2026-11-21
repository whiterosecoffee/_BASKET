# Multi-ticker relative valuation and rotation optimizer — proposed contract v0.1
Status: formal design and hand-calculated synthetic example; not implemented, live, backtested or trading-connected.
Origin: B15 #305. General engine owner: B04 #297 / PR298. This optical-theme node is a consumer specification, not a competing general engine. Compose existing engines/valuation/rotation/rotation.py at 56e9e03693cfcd71cf0ca04d50470332110defda, subject to owner review and compatibility. No duplicate ingestion, valuation forecasts or scheduler.

## Problem and hierarchy
A cheaper share price, larger drawdown or lower isolated P/E does not establish a better rotation. Ask: for the same dollars, account and dated horizon, does a feasible switch produce more net wealth than holding, and in which scenarios does that advantage disappear?
Parent capability: relative allocation under changing prices. Components:
1. Point-in-time input manifest (B02 quotes; issuer/B04 forecasts; account user input).
2. Common-horizon valuation adapter (B04).
3. Pairwise exchange and threshold engine (extend #297).
4. Scenario/portfolio action evaluator (B04 general capability, proposed).
5. Descriptive timing/traversal overlay (B06), independent of valuation.
6. Optical group specialization (B15): shared customer/fabric/laser concentration; conditional merger exposure.

Input/output contracts are explicit; a JSON file does not execute work. New proposed components remain planned until their owner accepts and develops them.

## Input contract
- run: as_of UTC, display zone, model revision/commit, manifest hash, USD base, endpoint dates, objective/hurdles, quote TTD and maximum cross-ticker timestamp skew.
- security: stable entity/instrument ID, ticker/venue, original currency, ADR/split conversion basis, security type, live corporate-action state, exposure group.
- quotes: executable bid/ask, sizes or depth when available, source/revision, session, observed_at, available_at, ingested_at, effective_at when applicable, expiry; adjusted historical prices on matching basis. Unknown required inputs suppress affected outputs.
- valuations: one row per ticker/endpoint/shared scenario. Terminal price, distributions and valuation method; GAAP/reconciled adjusted or other named earnings basis; diluted EPS and periods/calendar bridge; terminal multiple independent of current price; revenue/margin/dilution bridge and source versions. Forecast estimates/assumptions explicitly classified. Negative EPS -> P/E unavailable; use independently justified EV/revenue, EV/EBITDA with capex/debt, NAV or cash-flow method, else exclude valuation-dependent output.
- account: actual holdings and tax lots, cost basis and acquisition dates, cash/debt, account type, externally verified or explicitly hypothetical tax cash-flow schedule, financing rates, broker buying power/house maintenance rules, liquidity, concentration/group caps, trading windows, minimum equity/cash and settlement restrictions. Do not upload private account records to public GitHub. Prior conversation balances are not current inputs.
- frictions: quoted bid/ask already includes spread; add only incremental commission/slippage/impact. Borrowing/financing charged over modeled path. Model delayed/missed execution and adverse fill; never assume both legs at last trade.
- benchmark: explicit historical common anchor date and corporate-action basis for compression; no chosen peak dates that differ across tickers without labeling.
No input probability is inferred from a narrative. Probabilities require external sourced calibration and point-in-time validation.

## Outputs
1. Valuation table: ticker, executable price, common endpoint, diluted EPS/basis, forward multiple, terminal valuation range, annual/cumulative modeled return, source/freshness flags.
2. Directed rotation matrix: each row is held asset, column candidate. Cell reports after-friction net wealth edge versus holding for each scenario, executable exchange ratio, threshold gap, investable shares/residual cash, and eligible/blocked/unknown status. A->B need not be the inverse of B->A after frictions/taxes.
3. Threshold surfaces: maximum candidate ask at current held bid; minimum held bid at candidate ask; combinations clearing chosen wealth hurdle. Recompute for all pairs when prices change, subject to input validity.
4. Portfolio action frontier: hold and selected partial/full switches; endpoint wealth, downside scenario, cash/debt, concentration, turnover and maximum regret under declared scenarios. List nondominated alternatives; do not hide tradeoffs behind an opaque score.
5. Change attribution: price-only movement, EPS revisions for same earnings period, multiple assumptions, forecast roll, costs/taxes/financing and eligibility changes shown separately.
6. Audit: source/forecast snapshots, revisions and exclusions; all output as_of/version/expiry; one next required evidence item.

## Mathematical contract
For N held shares of A:
gross_held_today = N * bid_A.
net sale proceeds = N * bid_A - sale friction - tax cash reserved at actual payment timing, with signed tax inputs externally provided.
No automatic immediate cash credit for a tax loss. Mark deferred/uncertain benefits separately; do not assert wash-sale eligibility.
q_B = largest permitted share quantity with q_B*ask_B + purchase friction <= available proceeds.
cash_residual = available proceeds - q_B*ask_B - purchase friction.
W_hold(s,T) = common endpoint net account liquidation wealth under hold, including retained cash, distributions, debt/interest and terminal tax/cost conventions.
W_switch(s,T) = same endpoint/net-liquidation convention after switch, including cash_residual; any taxes already paid/reserved must be reconciled once.
edge(s,T) = W_switch/W_hold - 1, only if W_hold>0.
net cumulative return = W_action / initial common net liquidation wealth - 1; annualization uses actual elapsed dates and requires positive wealth.
Use the same tax/net liquidation convention for both alternatives. Distinguish tax reserve from cash paid: a reserved cash balance cannot be removed twice.
For the simplified fractional-share, no-tax/dividend/interest case with proportional sale cost c_s and purchase cost c_b, endpoint prices V_A,V_B and relative terminal hurdle h:
max_ask_B = bid_A*(1-c_s)*V_B / ((1+c_b)*(1+h)*V_A).
Equivalent ratio condition:
bid_A/ask_B >= (1+h)*(1+c_b)*V_A / ((1-c_s)*V_B).
This is a boundary, not a price prediction. Fixed fees, integer quantities, tax-lot selection and account constraints require the discrete cash ledger and numerical boundary search. Include residual cash, unlike the conservative v0 parent. Verify the boundary at a tick on both sides; valid tick sizes are instrument inputs.
For a partial switch, apply the same ledger to the sold quantity and keep unsold shares in W_action.

## Optimization contract
Universe: any eligible public instruments with comparable dated valuations; optical group is one reusable specialization. Candidate actions initially hold, cash, or 25/50/75/100% rotations from existing holdings, constrained to a declared finite grid. This is a finite candidate search, not proof of a global portfolio optimum. Wider combinations may be pruned but must disclose search coverage.
- Reject stale/incomparable inputs and infeasible actions before ranking; unknown account constraints mean unassessed, not safe.
- Evaluate actions using coupled scenarios: common AI capex/customer shock, margin and multiple compression, merger delay/failure and financing stress; do not pair every candidate bull with held bear.
- Report base edge, minimum scenario edge, downside endpoint loss, turnover, concentration and max regret. Define regret as max feasible W(a,s) - W(action,s) within the declared action set, at the same endpoint. A minimax-regret choice minimizes the largest dollar regret across supplied scenarios, without claiming scenario probabilities.
- Alternative explicit objectives: minimize regret; maximize worst-scenario wealth; or maximize calibrated expected net wealth with a user-selected risk penalty and supported probabilities. Do not silently swap objectives.
- Pareto dominance: action is no worse across all selected metrics/scenarios and better in at least one; display remaining tradeoffs. Hold/cash always remain candidates.
- Only call a rotation robust if it exceeds the selected hurdle in every required scenario AND all account checks pass; otherwise scenario-dependent. Missing scenarios prevent a robust label.
- No-trade band: entry hurdle exceeds exit hurdle; add turnover penalty/cooldown by policy to reduce churn. These parameters require validation and cannot guarantee return improvement.
- Margin: check buying power at execution and pathwise stressed equity/maintenance, concentration add-ons and minimums; endpoint survival alone is insufficient. Broker rules must be current. Correlation/exposure estimates require a declared source/window; unavailable is unknown.

## Synthetic example (not market data)
No taxes/dividends/financing; 1% proportional sale friction, zero added buy friction, whole shares; $10,000 initial gross capital. Hold 100 shares A at $100. Candidate B ask $50, C ask $80. Sale proceeds $9,900. Base endpoint prices A=$130, B=$75, C=$100. Stress endpoint A=$100, B=$45, C=$85.
| Action | New shares / cash | Base wealth | Base edge vs hold | Stress wealth | Stress edge vs hold |
|---|---|---:|---:|---:|---:|
| Hold A | 100 A / $0 | $13,000 | 0% | $10,000 | 0% |
| Sell 50 A, buy B | 50 A +99 B / $0 | $13,925 | +7.12% | $9,455 | -5.45% |
| Sell all A, buy B | 198 B / $0 | $14,850 | +14.23% | $8,910 | -10.90% |
| Sell all A, buy C | 123 C / $60 | $12,360 | -4.92% | $10,515 | +5.15% |
B wins the base comparison but does not dominate holding. C cushions this stress while trailing in base. An optimizer must expose this tradeoff.
For a 10% relative terminal hurdle, fractional-share max B ask is $51.9230769. With integer quantities and residual cash, exact boundary differs; use discrete evaluator, not this fractional result as an executable limit.

## Validation and acceptance for B04 implementation
A1 reuse #297 rather than duplicating it; support at least 3 securities, 2 common endpoints, 3 coupled scenarios and an explicit action set.
A2 same-price/no-growth identity loses only actual costs; both legs and residual cash reconcile; dividends/tax paid/debt interest counted once. Hold baseline remains feasible absent known invalidity.
A3 test all-pair directions, partial allocation, whole shares, tick boundary; tax-lot choice, missing tax inputs and non-immediate loss benefit.
A4 reject NaN/infinity/negative executable prices, stale/asynchronous quotes, forecast lookahead, mixed GAAP/adjusted EPS, mismatched calendar endpoints and unhandled split/ADR/currency basis.
A5 loss-making securities must not receive negative P/E bargain ranks; absent valid alternate valuation yields unknown.
A6 scenario coupling, no-trade policy, turnover and pathwise margin failure are visible; correlated group concentration is not treated as diversified merely because tickers differ.
A7 rerun same manifest deterministically; attribution reconciles changes; replay historical scenarios using only data available then, including costs and failed/missed fills, before claiming validated improvement.
No automatic trading, monitoring or performance claim from a design or fixture.

## Source and owner references
Existing implementation: https://github.com/whiterosecoffee/_BASKET/pull/298 .
Source timestamp/quotes: B02; valuation/calendar models and optimizer: B04; descriptive traversal/timing: B06; shared contract arbitration: B00; optical relationship/exposure proposals: B15/B05.
Fees: https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/updated
Margin house requirements: https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins-29
These regulatory pages support cost/account gating, not the tool's scenario assumptions or outputs.
