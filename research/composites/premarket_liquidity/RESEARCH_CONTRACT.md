# Premarket Liquidity & Capital Rotation — Research Contract v0.1 (proposal)

Status: **research specification only**; not a production engine, not an authenticated live feed, not a validated forecasting signal.
Spark: B17. Issue: #163. Branch: work/163-premarket-liquidity-rotation.
Exclusive file: `research/composites/premarket_liquidity/RESEARCH_CONTRACT.md`. No cross-owner edits.

## Objective
At a specified premarket decision time, describe (1) changes in investor fund allocations, (2) credit and funding stress, (3) market microstructure and breadth, (4) macro transmission, and (5) AI infrastructure financing exposure, without mistaking one for another. Benchmark incremental informational value against existing _BASKET B17 market context and B06 market geometry. USD default.

## Prior-art basis (independent sources)
1. **National accounts / stock-flow consistent accounting:** Federal Reserve Financial Accounts Z.1 distinguishes transaction flows, changes in valuation, and changes in asset/liability levels. https://www.federalreserve.gov/releases/z1/ (2026-Q2 release dated 2026-09-11); methodological explanatory notes https://www.federalreserve.gov/releases/z1/20241212/z1.pdf.
2. **Measured fund flows:** Investment Company Institute weekly estimated long-term mutual fund flows, revisions and ETF exclusions: https://www.ici.org/research/stats/flows. Use its separate combined/ETF/MMF releases according to coverage; avoid adding bond ETF net creation flows twice.
3. **Financial conditions index:** Chicago Fed NFCI combines risk, credit and leverage; weekly update does not establish a real-time daily observation. https://www.chicagofed.org/research/data/nfci/current-data.
4. **Market liquidity/microstructure:** Adrian, Fleming & Vogt, NY Fed Staff Report 827, revised 2023: spread, depth and price impact distinguish liquidity from volume. https://www.newyorkfed.org/research/staff_reports/sr827.html; Fleming, 'Measuring Treasury Market Liquidity' https://www.newyorkfed.org/research/staff_reports/sr133.html.
5. **Portfolio balance/liquidity preference and risk premia:** economic mechanisms/hypotheses only; do not infer observed transfers or causality from correlations.
6. **Factor / regime-switching / event study:** candidate inference methods; build simple, transparent deterministic benchmarks before HMM or dynamic factors; require frozen point-in-time walk-forward validation and ablation before an investable rating.

## Data semantics (nonnegotiable)
- Distinguish **fund net flows** (subscriptions minus redemptions in USD over reported interval), **money-market fund assets** (AUM stock level, change partly influenced by yield, distributions, reporting and definitions), **market dollar volume** (turnover, not net new investment), **Treasury issuance**, **ETF creations/redemptions**, **security price changes**, and **deposit/repo balances**. No raw sum of category values into a synthetic "money moved" figure.
- For any combined flow, identify fund universe, overlapping categories, reporting week, unit, revisions, signs and coverage. Never add a bond ETF subtotal to a 'bond funds plus ETFs' total.
- Time fields: effective_at/period_start/period_end, observed_at, first_available_at (publication), ingested_at, decision_as_of, expires_at/TTD, source URL/class, revision ID and optional original currency plus dated FX source/rate. A publication released after decision_as_of is prohibited in a premarket backtest.
- Status values: verified_current, verified_historical, delayed, stale, missing, disputed, provisional. No inference of zero from missing.
- For foreign exposures original currency retained; every headline USD conversion identifies FX effective/available time. Data publication lags are displayed separately from TTD; historical flow estimates can remain valid history without being current premarket evidence.

## Inputs and horizon layers
A. Weekly/daily published allocations: ICI MMF AUM and flows (distinguish change vs net flows), long-term fund and ETF bond/equity flows; optional EPFR if licensed; rolling 1/4/13 weeks with release and revision timestamps.
B. Rates and credit: 2y/10y Treasury levels/changes, curve, TIPS real yields, investment-grade/high-yield OAS, HYG and IEF as *market proxies* not direct investor subscription evidence; NFCI when available, SOFR/repo/funding conditions, bank reserves/TGA/RRP with definitional caveats.
C. Premarket market evidence: QQQ, SPY, RSP, SMH, IWM, NVDA, MSFT, AMZN, GOOG/GOOGL, CRWV, ORCL and AI-supply-chain basket; bid/ask, quote age, venue, dollar volume, relative strength, spread/depth (if entitled), broad breadth, futures reference times and synchronized data. Avoid treating a premarket quote from a prior date as today's.
D. Volatility and positioning: VIX, rates vol where licensed, credit pricing, options gamma/HIRO only if lawful data/provenance/expiry exist; positioning is *not* cash flow.
E. Event overlay: Fed auction/coupon settlement, FOMC/CPI/jobs/earnings, issuer contracts and financing with lifecycle stage and observed announcement time; separate known events from explanatory hypothesis.
F. AI financing: CRWV instrument maturity/covenants, refinancing and spreads, hyperscaler capex and supplier credit; use actual sourced disclosures or unknown.

## Proposed diagnostic transforms
- Normalize each flow within its reporting universe: USD amount, percent prior AUM, and robust historical percentile/z-score **only** where enough comparable observations and stable series definitions exist; show sample size.
- Directional persistence over 1/4/13 weeks, with last update age.
- Credit deterioration vs easing: spread-level, change and cross-market agreement, not blanket bond inflow = safety.
- Equity breadth: QQQ vs RSP/SPY and SMH/QQQ; market-relative returns synchronized at the identical decision clock.
- Divergence matrix: equity prices up while credit widens; MMF holdings rise while equity flows positive; Treasury demand strong while duration ETF prices decline; label as coexistence not proven transfer.
- Disaggregate allocation/credit/microstructure into independent component scores with missing-value coverage. Default output **five descriptive states**: risk_on_expansion, defensive_rotation, liquidity_accumulation, barbell_allocation, funding_stress; otherwise **indeterminate**. These are descriptive hypotheses; never claim future probability absent separate walk-forward calibration.

## Example machine-readable output interface (illustrative; not live)
```json
{
  "contract": "basket.premarket_liquidity.research@0.1",
  "status": "example_only",
  "decision_as_of": null,
  "session": "US_PREMARKET",
  "currency": "USD",
  "observations": {
    "money_market": {"assets_usd": null, "asset_change_usd": null, "net_flow_usd": null, "period_end": null, "first_available_at": null, "status": "missing"},
    "bond_funds_and_etfs": {"net_flow_usd": null, "period_end": null, "status": "missing"},
    "equity_funds_and_etfs": {"net_flow_usd": null, "period_end": null, "status": "missing"},
    "credit": {"hy_oas_bps": null, "change_5d_bps": null, "status": "missing"},
    "premarket": {"qqq_return_pct": null, "rsp_spy_relative_pct": null, "smh_qqq_relative_pct": null, "status": "missing"}
  },
  "components": {"allocations": null, "credit": null, "microstructure": null, "macro": null},
  "classification": "indeterminate",
  "confidence": "insufficient_data",
  "contradictions": [],
  "data_gaps": ["no_data_provided"],
  "validated_forecast": false
}
```
Final implementation contract/schema belongs to B00; this artifact is not normative schema.

## Decision display contract
First line: session and last observation timestamps; market-open/closed status using exchange calendar.
Second: cash allocation, equity/bond flow, spread change, index breadth and synchronized premarket dispersion each with source/freshness.
Third: **what changed vs prior report** (numeric delta and comparable interval), evidence supporting/against current descriptive state.
Fourth: scenarios with explicit triggers/falsifiers, trading costs/liquidity caveat, and one next evidence check.
No fabricated dollar inflows, directional probabilities, index weights, or forward returns.

## Validation / falsification
1. Unit arithmetic: overlapping ETF coverage, net flows vs AUM, units, FX and sign; duplicate releases/revision IDs; mismatched frequency.
2. Point-in-time replay: freeze publication and source availability, no future data; check holidays, Tokyo-vs-US session and partial premarket candles; prohibit stale quotes.
3. Deterministic unit fixtures for mixed/bullish/stressed/missing cases; null-aware outputs and explicit inconclusive result.
4. Compare against standalone B17 market context and B06 geometry on *same historical decisions*. Candidate metrics: calibration of categorical labels (only after definitions), balanced class accuracy, lead/lag false positives, drawdown and turnover under transaction costs; out-of-sample holdouts across stressed and quiet regimes.
5. Ablations: price/breadth only, +published fund flows, +credit, +rates, +microstructure. Demand positive out-of-sample incremental utility before adding complexity.
6. No live/service claim until B02 source entitlements, durable runtime and freshness contracts verified, B00 schema/ownership reconciled, B01 independent tests and current-main CI pass. Never claim alpha from a synthetic fixture.

## Dependencies and exact boundaries
- **B17** owns only this separate proposal. Reuse existing B17 market-context and macro-delta PRs, no modification.
- **B02** must own future adapters, revised point-in-time captures and freshness; see #148, #151/PR #153.
- **B06** must own market geometry/traversal, currently #149/PR #150. No duplicate returns or ranges here.
- **B00** arbitrates schema, shared contracts and orchestration; **B01** owns independent CI.
- Research paths outside this exact file and all production engines excluded. To implement, receiving owners need a scoped handoff and their own permissions; this file is **not** a deployment authorization.

## Receiver handoff (for orchestrator triage)
"Review B17 #163 and its draft research contract; reconcile with B17 #100/PR #101, #158/PR #159, B06 #149/PR #150, and B02 #148/#151. Assign source-entitled, timestamped published fund-flow ingestion to B02; existing geometry reuse to B06; any shared API schema to B00; independent point-in-time acceptance to B01. Preserve exact-owner paths and no-live/no-alpha guarantees. Do not open duplicate work without inspecting those existing issues; produce owner-specific contracts, tests and blockers."

## Disposition
Research contract complete when this exact file is committed and a draft PR is opened. Implementation, backtesting and production operation explicitly **pending**, not falsely declared complete.
