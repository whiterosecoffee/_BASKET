# Temporal relationships and relative value — tiered problem design
Design proposal November26,2026. Origin B15-305. Extends existing floating-rotation contract; does not create a new engine, canonical data store, task controller or scheduled job.
## Top-level problem
Determine whether a change in the exchange purchasing power between securities is an actionable improvement in durable future net wealth, a rational response to changed economics/risk, a common market move, or an observation/model error. Compare feasible holding/rotation alternatives over declared common horizons; uncertainty remains visible.
Separate three relationship families: economic links, empirical market dependence, and modeled relative valuation. None implies the others.

## Tier contracts
### L0: Evidence and comparability
Question: Can these observations be compared at this decision time?
Owner route: B02/B03 (proposed dependency, not an allocation).
Output: Immutable instrument/time/source manifest; stale/invalid exclusions.
Acceptance: Reject future-known inputs, stale quotes, wrong split/ADR/FX and different return conventions.

### L1: Economic relationship graph
Question: Why could one company affect another?
Owner route: B05 with ticker/B19 proposals (proposed dependency, not an allocation).
Output: Directed typed edges with exposure, terms, effective dates and evidence.
Acceptance: Separate verified contract/ownership from shared-customer exposure or hypothesized pass-through; avoid spend double counting.

### L2: Business economics and normalization
Question: What earnings and cash does each business actually retain?
Owner route: Ticker owners / B04 (proposed dependency, not an allocation).
Output: Segment demand→capacity→revenue→margin→cash→diluted recurring EPS.
Acceptance: Reconcile reported to recurring earnings, SBC, financing and economic reinvestment; no P/E ranking for negative EPS.

### L3: Market relationship and attribution
Question: Which movement is common exposure and which is issuer-specific?
Owner route: B06/B04/B07 (proposed dependency, not an allocation).
Output: Multiwindow return correlation, beta, downside dependence, factor residual and stability flags.
Acceptance: Use synchronized returns not correlated trending price levels; separate sessions; report estimation error and effective sample.

### L4: Comparable valuation and relative-value change
Question: Did market price change, economics change, or the valuation convention change?
Owner route: B04 (proposed dependency, not an allocation).
Output: Common-horizon value ranges, discount ratios, current/frozen baseline index and revision attribution.
Acceptance: Separate fixed-endpoint from rolling NTM views; company-specific multiples under common macro assumptions; reconcile revision/FX/horizon effects.

### L5: Persistence, regime and event diagnosis
Question: Is divergence temporary, structural, or not identifiable?
Owner route: B06/B07/B21 (proposed dependency, not an allocation).
Output: Event-aligned residual paths, break flags, competing explanations and falsifiers.
Acceptance: No mean-reversion or lead-lag claim without stability and out-of-sample evidence; lagged association is not causation.

### L6: Net portfolio decision
Question: Does a feasible action improve the account relative to holding?
Owner route: B04/B17 (proposed dependency, not an allocation).
Output: Hold/cash/partial/full action frontier, net wealth ranges and two-way price thresholds.
Acceptance: Include both legs, cash, distributions, tax timing, financing, concentration and pathwise margin; no action from incomplete required inputs.

### L7: Evaluation and controlled maturation
Question: Does the method work beyond the examples used to design it?
Owner route: B07/B01 (proposed dependency, not an allocation).
Output: Point-in-time walk-forward results, rejected signals, benchmark comparison and acceptance receipt.
Acceptance: Include delisted/failed cases, missed fills, costs, multiple-testing control and untouched holdout; synthetic checks do not demonstrate trading advantage.

Governance is orthogonal: one owner per artifact, source/forecast/model revision, exact-revision evidence, review and adoption state. These are logical capabilities and issue tiers, not instructions to create eight branches. Reuse #297/#311 and existing source owners; allocate only the smallest work item actually launched.

## Temporal data method
Use canonical stores by reference. Append immutable observations/corrections. Every link/fact carries valid_from/valid_to or effective_at plus first-known available_at and recorded/ingested_at; unknown timestamps stay unknown. Support historical queries both 'valid in the world at t' and 'known to the system by t'. Corrected later data cannot replace the original record in a historical decision replay.
Store prices separately from fundamentals, event calendars, relationship edges and computed runs. An event has announcement/publication time, fiscal period_end, expected/confirmed report date and possible implementation date; do not collapse them.
A computation records source revisions, eligibility/freshness policy, horizon definition, scenario/config and code hash. Quote freshness expires quickly; historical source truth and estimates have different validity policies. Economic edge absent or confidential means unknown, not zero exposure.
Intraday and investment-time streams are distinct: matched bid/ask and liquidity for entry; daily total returns/factors for dependence; release-by-release forecast versions for valuation. Never mix current US ADR prices with an asynchronous Korean close without labeling venue/FX uncertainty.

## What to track per company, pair and group
Company: price/total return, recurring diluted EPS and estimate dispersion, FCF/share, financing/debt maturity, valuation ranges, factor exposure and event risks.
Pair: directed executable exchange ratios both ways; earnings/cash purchased; common-horizon relative discount; factor-residual divergence; uncertainty and evidence state.
Group: shared customer/funding/supplier exposures, concentration and covariance, aggregate portfolio outcomes. Do not confuse many correlated pairs with diversified opportunities or independent signals. Source/input updates fan out to affected pairs; do not refetch identical inputs per pair.
For SNDK/CRWV, common AI-spend exposure is not proof of a direct supply contract. Positive memory pricing can help a manufacturer while raising infrastructure input cost; contract terms determine magnitude/timing. This is a hypothesis until exposure and pass-through evidence exist.
For SNDK/SKHY, ADR ratio/FX/earnings normalization is prerequisite. A persistent geographic/venue premium can be structural rather than an executable arbitrage.
For semiconductor/memory vETFs, use configuration-level constituents, benchmark and constraints; reuse one engine.

## Descriptive versus explanatory metrics
Begin with synchronized total-return changes, ratio changes, realized volatility, upside/downside beta and rolling or exponentially weighted correlations over declared windows. Use arithmetic returns for portfolio P&L and log returns where appropriate for additive attribution. Distributions and corporate actions handled explicitly.
Estimate a parsimonious factor model r_i=alpha_i+beta_i'X+epsilon_i with broad market, sector, rates/credit/FX where economically supported. Avoid collinear QQQ/SMH/market regressors or excessive parameters for the sample; shrink covariance and assess factor stability if needed. Residual means unexplained by this model, not proven mispricing.
Compare issuer residuals and event-relative paths. Test whether a demand/revenue/earnings change warrants the observed price move. Do not use a three-session intraday correlation as stable long-run dependence.
Cointegration is optional prior art for log-price spreads after integration-order, residual stability, break and out-of-sample checks. The economic model need not assume a stationary spread. A z-score or cointegration rejection test does not establish profitable convergence. Refit only with information available then; estimate half-life only if evidence supports it. Track relation failure as a first-class state.

## Valuation change ledger
Maintain fixed-calendar and rolling-forward horizons separately. For positive earnings using a fixed EPS period and a consistent multiple convention:
change log P = change log EPS + change log implied P/E.
This is accounting attribution, not causal proof. Add an explicitly separate FX/ADR conversion term for foreign earnings; handle NTM window roll outside the same-period EPS revision. Negative/nearzero EPS makes this log decomposition invalid.
Use matching equity valuation methods: normalized earnings and cash conversion for profitable issuers; FCFF with explicit EV→equity bridge or APV/funding scenarios for highly levered capacity businesses. Terminal equity values must include dilution/debt/refinancing assumptions; a target price is not a current intrinsic value without time/risk conventions.
Let F_AB(t,T,s)=V_A(t,T,s)/V_B(t,T,s); R_AB(t)=bid_A/ask_B; I_AB=100R_AB/F_AB. This price-only index compares gross terminal stock value under scenario s. Net wealth comparisons supersede it when distributions, frictions and taxes differ.
Track log I change as log R change minus log F change. Decompose F movement through earnings/cash revisions, discount rates/relative multiples, dilution, FX and horizon roll. For nonlinear models use frozen-input revaluation or declared Shapley allocation; disclose interaction/order effects and reconcile total change. Do not invent additive causal contributions.
Keep immutable original-forecast and latest-forecast views alongside current/frozen fair-ratio indices. Never move the fair-ratio anchor invisibly to explain an unsuccessful signal after the fact.

## Decision states and uncertainty
States: incomparable; observation-only; explained repricing; unexplained divergence; candidate; blocked; scenario-robust or scenario-dependent action; invalidated. These are evidence labels, not probability buckets.
Evaluate paired/coupled shocks, not candidate bull against held bear. Report range of net advantages and downside/regret versus hold. Robust edge requires a declared scenario set; scenario weights only with justified calibration or explicit user preference.
Keep no-trade region and distinct entry/reversal thresholds. Marginal expected improvement must exceed costs and model uncertainty, with an explicit exposure/turnover budget. Holding and cash are real alternatives. Tax benefit availability and margin feasibility must be privately verified, not inferred from historical conversation positions.
Separate valuation edge from execution timing: tape can qualify a fill; it cannot prove fundamental value. A strong rebound does not create cheaper future earnings by itself.

## Prior-art families and adoption
1. Temporal databases/event sourcing/knowledge graphs: immutable facts, valid time versus known time, revision lineage and typed exposure edges. Adopt conceptual contracts, not a new database by default.
2. Accounting, DCF/APV and fundamental relative valuation: separate cash flow/growth/reinvestment/financing from pricing conventions. NYU primary source https://pages.stern.nyu.edu/adamodar/New_Home_Page/littlebook/intrinsicvsrelative.htm .
3. Multifactor equity risk and attribution: distinguish shared style/sector/macro exposures from issuer residuals. MSCI primary source https://www.msci.com/data-and-analytics/factor-investing/equity-factor-models .
4. Econometrics/event studies/state-space/break detection: conditional dependence, regime instability and explicit counterfactual limitations. statsmodels cointegration https://www.statsmodels.org/dev/generated/statsmodels.tsa.stattools.coint.html and recursive diagnostics https://www.statsmodels.org/dev/generated/statsmodels.regression.recursive_ls.RecursiveLSResults.cusum.html .
5. Portfolio control/transaction-cost-aware optimization: optimize net outcomes with holdings state rather than rank raw upside. Stanford source https://web.stanford.edu/~boyd/papers/cvx_portfolio.html and Cvxportfolio costs https://www.cvxportfolio.com/en/stable/costs.html .
6. Forecast evaluation/decision science: calibration, sensitivity, benchmark-relative regret and point-in-time walk-forward evaluation. Treat retrospective best switching dates as oracle upper bounds, not a deployable strategy.
7. Software contracts/workflow evaluation: source-pinned runs, deterministic calculations, narrow stories, explicit checkpoint/receiver evidence. Reuse _PATTERNS/_AGENTIC_AGILE, _AGENT_FRAMEWORK and _GROUP_MONITORING via canonical receipts rather than installing/rebuilding a runtime.

## Bounded issue sequence and outputs
First: B04 adopts/qualifies tested freshness/basis/endpoint/cash proposal from review PR313. Not yet an adopted fix.
Second: define source manifest and one fixed-endpoint two-company value revision ledger; output historical/frozen/current comparison with explicit missing data.
Third: add factor-residual view and event overlays on validated histories; make structural-break/unknown states visible before proposing mean-reversion timing.
Fourth: add net action frontier/two-way bands and point-in-time replay against hold/simple rebalance. Expand two-pair/two-group fixtures only when prior checks pass.
Deliverables: this design, problems.json hierarchy, source references in local AGENTS/state, and owner-routed acceptance examples. No new top-level shared schema/registry/branch or runtime is created by a problem definition.
