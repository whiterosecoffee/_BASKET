# B17 virtual ETF — approved decisions, minimal implementation and cross-owner dependencies

**As-of:** 2026-11-03 · **Issue:** #118 · **Branch:** `work/118-skilled-ai-deployment-basket` · **Draft PR:** #120  
**Status:** Design + provisional B17 research and capped-weight component; not validated as an investable portfolio.

## Explicit decisions

| Decision | Binding choice |
|---|---|
| Primary objective | Maximum **risk-adjusted share-price appreciation**; do not select on absolute speculative upside alone |
| Universe | All U.S.-tradable listed companies and ADRs; market cap affects liquidity, risk and conviction rather than eligibility by hard cutoff |
| Reweight policy | Monthly plus materially new public earnings/contract/financing evidence; evaluate changes first, trade only above uncertainty/turnover buffer |
| First output | Ranked **end-2026, end-2027, end-2028** conditional valuation chart plus frozen, explicitly paper-only basket |

**Important:** Risk-adjusted winners require empirical downside, correlation and calibration evidence. Until such evidence exists, display scenario ranges and a nondominated/Pareto comparison, not a false unique optimal score.

## Reuse first, no duplicate implementation

| Responsibility | Existing work | B17 consumption | Write owner |
|---|---|---|---|
| Identity / membership contract | B00 #119, #130, #146, #148 | Venue/ADR canonical references, versioned basket membership | B00 and assigned ticker owners |
| Forward valuation and ETF comparisons | B04 #126 / PR #127 | Dated EPS/FCF, bull/base/bear year-end values, stress and Pareto outputs | B04 |
| Price/FX/source freshness | B02 data work + #148 migration | Normalized evidence manifest, only valid USD/FX values | B02 |
| Broad market-context composite | B17 #100 / PR #101 | Optional relative macro/traversal flags, no duplicate engine | #100 worker |
| CI & independent acceptance | B01 #129 for B04; separate targeted B17 exact-head suite | Pass/fail at PR #120 latest SHA, negative fixtures and replay | B01 |
| Narrative and calibration | B21 and B07 | Hypothesis falsifiers and out-of-sample performance audit | respective owners |
| Execution queue | B00 #136 | Link scoped issue #118 and handoffs; no second task ledger | B00 |

## Data contract B17 requests (do not duplicate canonical facts)

**Inputs (read-only references):**
- `universe_snapshot_id`, basket membership revision, issuer `instrument_id` and venue/MIC, ADR and parent mapping, candidate/member/adjacent/excluded status.
- As-of `observed_at`, `effective_at`, `available_at`, `ingested_at`, `expires_at`, original currency, dated USD conversion and source class, provider entitlement, source hash.
- Year-specific 2026/2027/2028 EPS/FCF scenarios and assumptions, GAAP versus adjusted basis, shares/dilution, debt/cash, dividends, model version and risk inputs.
- Explicit missing/contradictory/provisional flags; no implicit fill from adjacent periods.

**Outputs (B17 owned):**
- Versioned `basket_snapshot_id`, `as_of` and input-manifest hash.
- Ordered per-ticker year-end 2026/2027/2028 conditional values in USD, upside/downside versus synchronized price, scenario/consensus labels and missing coverage.
- Candidate eligibility and rejection codes; ranked conditional multi-objective comparisons when risk skill unknown.
- Paper weights, reserved cash, segment/issuer/ADR overlap controls, transaction-cost/slippage assumptions, planned turnover and rebalance delta versus prior frozen snapshot.
- No live execution, actual return or predictive probability claim until independent validation.

## Minimal vertical slices (in order)

1. **M0 — Contract and integrity.** Make issue #118 scope authoritative; review overlapping PR file diffs. Keep the existing `basket.json`, `virtual_etf_policy.py` and its tests. Freeze a fixture/input contract. Evaluate whether scores without actual forward forecast quality should remain excluded or strictly labeled heuristic. **Do not inflate score confidence.**
2. **M1 — One real input record.** B02/B04 produce one eligible US ticker and one ADR with source-backed same-cutoff price, FX, EPS/FCF scenarios, freshness and security ID. B17 read-only consumes them. Evidence includes negative stale/unknown and cross-currency tests.
3. **M2 — First ranked chart.** Show the existing six-company research pilot as provisional historical data and a separate validated comparison only for symbols with complete M1 coverage. Three independent year-end values, assumptions and explicit range, sorted by selected horizon. Unavailable = null.
4. **M3 — First paper portfolio.** With >=2 independently sourced eligible securities, issue frozen composition/weight snapshot (not an automated trade). Score and cap by company, segment and correlated exposures; cash allowed. Report baseline, estimated costs and reasons for rebalance.
5. **M4 — Walk-forward and economic validation.** B07/B01 independently replay vintage forecasts and decisions; benchmark against QQQ/SPY and naive equal-weight; assess skill, drawdown, cost drag and portfolio turnover. No claims of alpha before this passes.
6. **M5 — Production scheduling (deferred).** B08 only if source runtime, persistence, identity resolver and expiry/CI have passed and user wants active monitoring.

## Acceptance / failure tests

- Same input manifest and model version produce identical scenario and weights; no future earnings estimate enters past snapshot.
- Reject stale or unentitled quotes, missing ADR FX, unknown venue/ID, invalid negative price, mixed adjusted/GAAP EPS bases and reused inaccurate release dates.
- Ensure sum(weights)+cash=100%; cap per name <=15% and per economic segment <=35% unless later explicitly versioned; separate issuer/ADR duplicate economic ownership and parent look-through.
- Avoid hardcoded market cap eligibility, hardcoded company ranks, automatic admission of newly profiled ticker, or invented default EPS.
- Freeze target and actual paper-state separately; include dividends/splits and estimated costs when calculating returns. Material event signals evaluation, **not forced turnover**.
- Run domain tests and independent B01 exact-head tests on current PR SHA; do not count code inspection, JSON parsing or outdated green CI as acceptance.
- Review user-facing top-level chart order, specified as best conditional **2028** model upside by default with separate 2027 and 2026 columns, but **do not label as risk-adjusted leader** until backtested/cross-name uncertainty is calibrated.

## Deliverable boundaries

**B17 write:** `research/composites/skilled_ai_deployment/**`; `engines/composites/virtual_etf_policy.py` and test file, only once #118's revised scope is reviewed.  
**B17 read:** issuer, market data, B04 valuation, B06 traversal, B17 #100 market-context, shared architecture.  
**B17 never write:** `_TICKERS/**`, `tickers/**`, `research/<TICKER>/**`, `schemas/**`, `orchestration/**`, `engines/valuation/**`, shared CI, provider API or runtime.  
**Current limitation:** `_TICKERS` is a staging registry under B00 PR #147/#148, **not yet a verified canonical write destination**.

## Current blockers and single next action

**Blockers:** shared basket/ticker contracts B00 #119/#148; source-backed dated B02 inputs; B04 price/earnings forecasts and risk review; independently executed B01 exact-head test evidence. B17 PR #120 has older history and requires diff/CI refresh after dependency alignment.

**Next action:** B00 review the revised #118 and existing #119/#136 queue, select owner-specific contract acceptance; B01 test the latest PR #120 SHA while B17 independently reviews and normalizes its provisional artifact quality. No auto-merge.
