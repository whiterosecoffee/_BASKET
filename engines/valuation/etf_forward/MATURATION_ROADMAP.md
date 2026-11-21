# ETF forward valuation — broad maturation roadmap and quality baseline

**Date:** 2026-11-04. **Owner:** B04, issue #126, draft PR #127. **Exclusive permitted writes:** `engines/valuation/etf_forward/**`. **Architecture:** core v0.4.1 declared; v0.5.0 is an unreleased candidate. **Scope:** company portfolio optimization versus ETFs for **highest risk-adjusted share-price appreciation**, with **2027 and 2028 ranked independently**.

## Current baseline — assessment rubric

These are **subjective engineering maturity assessments**, not market model-validation scores. Each domain scores 0 (absent), 1 (proposal or weak prototype), 2 (initial functioning component), 3 (bounded testable API), 4 (independent point-in-time tests and verified real sources), 5 (production-grade documented integration and adverse-case evidence). Evaluated against B04 PR #127 **before this milestone's risk module**.

| Domain | Baseline /5 | Target /5 | Proof needed |
|---|---:|---:|---|
| Modular architecture | 3 | 5 | Stable versioned contracts, independent consumers |
| Earnings valuation mathematics | 2 | 5 | Cross-check economic ownership vs look-through earnings, signed earnings |
| Holdings/ETF accounting | 2 | 5 | Dated full fund holdings, cash/derivatives/ADR/fees |
| Provenance and source trust | 2 | 5 | Source SHA, availability, contradictory data behavior |
| Point-in-time integrity | 2 | 5 | Historical vintage and correction replay, no lookahead |
| 2027/2028 real fundamentals | 0 | 5 | Calendarized sourced estimates and coverage |
| Scenario/valuation decomposition | 3 | 5 | Gross/net, interaction, fees, counterfactuals |
| Measured historical portfolio risk | 0 | 5 | Matched-date total returns, drawdown, volatility, downside beta |
| Constrained portfolio optimization | 1 | 5 | Ex-ante optimization and feasible Pareto frontier |
| Walk-forward validation | 0 | 5 | Holdout, survivorship-free historical tests |
| Domain/independent CI | 1 | 5 | Latest PR exact-head green CI with adverse fixtures |
| Investment decision reports | 2 | 5 | Dated sourced dual-horizon report with falsifiers |
| **Total** | **18/60** | **60/60** | All gates independently demonstrated |

**Why not score model accuracy?** No out-of-sample model measurements exist, and no synthetic test can establish predictive performance. No increase in these baseline scores should be claimed merely from adding code.

## Prior-art families to reuse rather than duplicate

1. **Portfolio theory:** mean-variance, lower-partial-moment and drawdown measures; use *observed* risk, not retrospective optimal weights as if ex-ante.
2. **Multi-objective optimization:** Pareto non-dominance; avoid one arbitrary risk/return scalar before metric semantics are agreed and validated.
3. **Point-in-time data systems:** availability-aware temporal joins, source manifests, immutable revisions, correction replay, vintage and TTD validation.
4. **Fund accounting:** issuer economic weights, look-through earnings yield, handling negative earnings and non-equity positions, expense/tracking reconciliation.
5. **Financial return attribution:** earnings growth × multiple-change identity with interaction; dividends, costs and composition changes separate.
6. **Backtest discipline:** purged/rolling walk-forward, locked parameters, benchmark and execution-cost stress, survivorship/no-lookahead tests.
7. **Hexagonal architecture and contract testing:** data adapters supply evidence, B04 remains pure deterministic math; version inputs/outputs and no cross-owner code edits.

## Ranked delivery sequence and dependency-ordered exit gates

### P0 — Integrity and test baseline (B04 + B01; immediate)

- Execute ALL existing B04 tests at latest PR head, not obsolete SHA in old handoffs.
- Repair material numerical defects and explicitly distinguish equity estimate coverage from full economic fund weight and derivatives/cash.
- Invalid/negative earnings must be retained in earnings yield yet P/E must be null when nonpositive/incomplete.
- Reject future-known weights/estimates, duplicate holdings, invalid non-USD unit conversion and incompatible source snapshots.
- **Exit:** independent exact-head B01 CI #129 with pass/fail evidence and a documented issue list. Partial local tests do not close P0.

### P1 — Observed-risk and trade-off core (B04; this commit)

- New `risk_frontier.py`: aligned daily returns, portfolio total-return volatility, downside deviation, maximum drawdown, downside beta; all require as-of-known observations and explicit daily-constant-weight policy.
- Separate 2027/2028 `pareto_frontier()`: maximize conditional appreciation while minimizing stress loss, measured drawdown, trading costs and concentration; no probabilities or scalar score.
- New `test_risk_frontier.py`: adversarial tests for missing/reordered sessions, insufficient history, lookahead, weights, negative returns, portfolio duplicates, horizon mixing, dominance and tradeoffs.
- **Local evidence:** 16/16 tests passed on a local reconstructed equivalent using Python unittest on 2026-11-04. NOT an exact-head GitHub checkout or independent CI.
- **Exit:** B01 independently reproduces latest PR head; B04 connects observed data with source manifests; Pareto does not imply expected returns or optimal forecast.

### P2 — Canonical source contracts (B00 + B02 + B03; #128)

- Read existing ticker-home migration #148, not add an ETF holdings store within B04.
- B00 assigns single canonical owner for issuer holdings and consensus estimates. B02 supplies synchronized prices/FX/market history; B03 supplies official issuer filings and separately provenance-labeled consensus.
- Preserve `effective_at`, `observed_at`, `available_at`, `ingested_at`, revision/source class/TTD, original currencies and date-matched FX.
- **Exit:** 100% holdings reconciliation where available, economically defined earnings-coverage fractions, no historical lookahead and reproducible manifest digests. Missing consensus explicitly unrankable.

### P3 — Dual-horizon and portfolio selection (B04 + B17)

- Compare actual fund benchmarks **SMH, SOXX, XSD, QQQ, QQQM, SPY, VOO, RSP, XLK, VGT, SCHG, IGV, IWM, AIQ and AIEQ** (later expansion conditional on authoritative issuer coverage). Do not confuse AIEQ (AI-selected cross-sector equity) with AIQ (AI technology thematic exposure).
- Optimize permitted U.S.-tradable individual issuers, including NASDAQ/NYSE/ADRs. No fabricated ETF membership for separately researched basket tickers.
- Publish separate 2027 and 2028 Pareto sets and conditional absolute-upside diagnostics. Make sector/single-name caps, rebalance assumptions and trading costs explicit.
- **Exit:** at least five ETFs + four-name illustrative basket + optimized portfolios validated at both horizons, with constituent attribution and locked source vintages.

### P4 — Market regime overlays (B06 + B17 + B02; read-only B04 consumers)

- Use existing Treasury/credit, QQQ-SPY-relative, VIX, market-volume liquidity, options gamma and macro composites. Never add correlated HIRO exposures as independent signals.
- Separate liquidation, multiple reset, earnings deterioration and systemic credit stress, with supporting/contradictory evidence.
- **Exit:** dated source-verified regime evidence changes only the conditional analysis assumptions; it does not magically create earnings forecasts.

### P5 — Historical falsification and risk calibration (B07 + B01 + B04)

- October 30, 2026 SMH issuer-weighted attribution must reproduce synchronized close/NAV (Intel, AMD, NVDA, TSM and remainder).
- Walk-forward from eligible historical dates using then-known constituents, estimates, prices and realistic transaction costs. Evaluate drawdown, downside beta, volatility, trading frictions, sensitivity and missed recoveries.
- Falsify high-EPS-growth/low-return cases, reversal after gamma recapture, cyclically peak profits and ETF-vs-basket superiority.
- **Exit:** held-out risk-adjusted results with sample sizes, uncertainty and failure examples; no predictive ranking before validation.

### P6 — Review, production and release (B00 + B01)

- B00 reconciles issue #136 canonical queue, ownership, active changed files, branches and dependencies; do not create another task database.
- Only B01 writes shared CI/integration tests, only B00 shared schemas/orchestration, only B02 market feed/FX and only B03 issuer event research.
- **Exit:** exact-head CI, reviewed B04 PR, B00 approved contracts and explicit user approval for merge/release. Component verified ≠ integrated.

## Future scoring and go/no-go standard

- Re-score each dimension only with linked code/fixture/tests/sourced data evidence. Distinguish local test, GitHub CI exact SHA, integrated main and release.
- **MVP usable for investment comparison:** P0–P3 gates satisfied; P4 regime support optional for explanatory use.
- **Risk-adjusted winner claim:** P0–P5 gates and justified choice of empirical risk metric. Otherwise present Pareto frontier, missing-data status and invalidation conditions.
- Avoid expanding universe or adding scoring weights before verified evaluation demonstrates value.

## Orchestrator receiver handoff

Resume B00 issue #136, not a new orchestrator/queue. Inspect live #126/#127 latest head, #128/#129, #148/PR147, B06/B17/B07 active work and B04 owned paths. The user selected risk-adjusted individual-company portfolio appreciation versus ETFs for two separate end-2027/2028 horizons. Keep B04 math under `engines/valuation/etf_forward/**`; register P0–P6 as linked acceptance gates, assign B01 exact-head CI and B00 canonical ETF/consensus ownership, then B02/B03 real historical inputs, B06/B17 regimes and B07 falsification. Respect the 3–5 active-worker limit and avoid duplicate services, worker branches, issues and data stores. Do not treat local synthetic tests as production proof, and never merge without explicit user authorization. **One next action:** B01 rerun all B04 tests at latest PR #127 SHA and post exact results.
