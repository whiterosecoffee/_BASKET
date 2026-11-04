# B04 ETF vs constituent-portfolio optimization plan

**Decision recorded:** 2026-11-03. **Issue:** #126. **Draft PR:** #127. **Spark:** B04. **Owned paths:** `engines/valuation/etf_forward/**`. This is a design/acceptance update; it does not claim implemented optimization or market-data availability.

## Locked user decisions

1. **Objective:** highest **risk-adjusted share-price appreciation**; absolute-upside ranking is a secondary diagnostic, never the sole winner criterion.
2. **Investment competition:** build optimized individual-company portfolios and compare them against actual ETFs (SMH, SOXX, XSD, QQQ, SPY initially; expand later).
3. **Horizon:** separate end-2027 and end-2028 results, using as-of-known, appropriately calendarized financials; avoid combining horizons into one unexplained score.

## Minimum viable comparison unit

`versioned constituent inputs + permitted portfolio constraints + one as-of snapshot + one horizon -> scenario/risk matrix + attribution + coverage + provenance`.

This deterministic unit composes into portfolio search without copying raw histories. Single responsibility: evaluate a portfolio; ranking/optimizer consumes evaluated results. No duplicate ingestion, ETF registry, ticker record store, traversal, or shared schema.

### Candidate construction

- Begin with all eligible ETF constituents plus a separately flagged research basket. NEVER mislabel non-constituents as ETF holdings.
- Compare baseline actual ETF positions, actual ETF holdings replicated with costs, equal-weight benchmark, a four-name **illustrative** NVDA/TSM/AVGO/KLAC basket, and reproducibly selected candidate company portfolios.
- Define objective and eligibility before optimization, never select winners from realized future returns.
- Constraints: maximum single-name/sector concentration, liquidity/minimum tradability, currency/ADR eligibility, maximum turnover, estimated execution costs and fees; expose tunable values with sensitivity, do not invent a user's risk limits.
- Risk measures: realized volatility, downside deviation/Sortino-style ratio only where sample adequate, maximum drawdown, beta/downside beta, stress-case loss, turnover, concentration and exposure overlap. Use multiple measured/conditional risks rather than conflating predicted volatility with stress downside.
- A true risk-adjusted ranking needs an explicit objective with units and calibrated/validated inputs. Until agreed and empirically measured, publish a **Pareto frontier** (conditional upside vs downside loss vs concentration vs trading costs) with no fabricated scalar score or statistical probabilities. Sort scenario outputs only as scenarios.

### Valuation and scenario contract

For each horizon `2027`, `2028` independently: complete economic weights, dollar-denominated net-income/market-cap yields, negative earnings accounting, fiscal-to-calendar conversion, estimate dispersion/revision vintages, EPS dilution, financing exposure, capital intensity, and a conditional earnings/multiple/interaction price-return decomposition. Show cash/dividends/fees/turnover and tracking as separable terms. Reflect dynamic rebalances only with explicit dated rules and realistic execution assumptions; fixed-weight static attribution is not equivalent to ETF historical total return.

Require a date-matched source manifest with `effective_at`, `observed_at`, `available_at`, `ingested_at` as supported, expiry status, FX venue and source class. Preserve unknown fields as missing and fail closed when consequential. Historical holdings/estimates must be known at replay time.

### Falsification / evaluation

- No current holdings substituted for historical holdings; assert look-ahead rejection.
- Negative earnings, incomplete portfolio coverage, derivative/cash positions, ADR class collisions, foreign FX and stale estimates must not yield unsupported P/E.
- Invariant: weights reconcile; attribution sums to return within explicit tolerance after fees and costs; scenarios have identical as-of and units.
- Test optimistic +80% EPS with -40% multiple (only +8% before costs), +50% EPS with -40% multiple (-10%), and a lower-growth security with favorable valuation.
- Holdout walk-forward historical comparisons across ETFs, equal weights, four-name illustrative basket and independently selected company portfolios; report gross/net performance, overfitting, survivorship, regime dependence, missed rebounds and sensitivity to transaction costs.
- Prohibit calibrated probability, optimal risk-adjusted winner or point price target until real evidence supports it.

## Dependency/ownership gates

- **B00:** resolve #128 data-contract ownership and proposed `_TICKERS/` migration #148/PR147, shared schema and queue. Existing issue #136 is the orchestrator's canonical queue; do not establish a new queue here.
- **B01:** #129 execute all B04-owned tests on the **latest** PR head, not the obsolete initial SHA; independently validate metrics and CI.
- **B02:** source synchronized prices, ETF histories, FX, dated issuer holdings only via approved data contracts (no B04 writes).
- **B03:** issuer SEC/IR earnings and revisions; consensus provider provenance is a distinct contract with B00 ownership arbitration.
- **B06:** existing market geometry and traversal are read-only descriptive overlays.
- **B17:** contextual macro/sector concentration and overlap inputs, without double-counting index constituents.
- **B07:** out-of-sample evaluation and calibration only once reproducible point-in-time evidence exists.

## Incremental milestones / acceptance

**M0 correctness:** execute existing tests at latest head; repair flaws in yields, P/E null states, ETF cash/derivatives handling, scenario and fee math. Exact independent evidence.

**M1 narrow data contract:** pinned full issuer holdings, date-matched prices/FX, and 2027/2028 estimates with coverage. Unknowns remain null. Do not treat a synthetic fixture as observed.

**M2 independently reusable portfolio-evaluation unit:** deterministic reports for one portfolio per horizon, explicit objective inputs and Pareto comparisons; duplicate-free source links.

**M3 actual ETF-versus-company competition:** for both horizons compare SMH/SOXX/XSD/QQQ/SPY, four-name example, equal-weight and optimized constituent baskets with out-of-sample constraints.

**M4 retrospective attribution:** October 30, 2026 SMH issuer-weighted price-return reconciliation and composition effects, with dated available holdings and synchronized closes.

**M5 historical validation:** walk-forward/out-of-sample tests with risk measurement and falsifiers; compare economic return versus valuation-only performance.

**M6 review/integration:** B01 exact-head CI, B00 dependency approval, draft PR; never merge without explicit user authorization.

### Report fields

Two separate ranking tables (2027 and 2028), plus conditional maximum-upside comparison. Fields: ticker/ETF or company basket, weights/rebalance rule, forward earnings growth, earnings yield/PE and estimate coverage, conditional upside, stress downside, observed risk metrics when sufficient, costs, issuer overlap, evidence/TTD, invalidation, uncertainty and Pareto dominance. If unavailable, report **unrankable**.

**Next action:** B01 execute and verify the latest #127 head tests while B04 repairs accounting semantics in exclusive subtree. No additional worker launched by this plan.
