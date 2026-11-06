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


## Unified PRE/RTH/AH session-aware extension (2026-11-06; issue #163 revised)

**Architecture decision:** one common market context/analysis engine, three exchange-calendar-derived session profiles, one canonical observation history. This research module supplies macro allocation/credit context; it DOES NOT reimplement B06 market geometry or B02 ingestion. This is an extension of the current B17 research proposal, not authorization to create a separate 'premarket engine'.

### Session contract and acceptance logic
- Trading calendar: US equities exchange-specific schedule in America/New_York, timezone-aware timestamps and DST; PRE 04:00–09:30 ET, RTH 09:30–16:00 ET, AH 16:00–20:00 ET for typical eligible US-stock extended-hours data. Trading availability, holidays, half days, exchange suspensions and broker-specific access override simplistic clock windows; session derivation belongs to canonical B02 adapter/B00 contract.
- Session tags: `PRE`, `RTH`, `AH`, `CLOSED` as derived output, NEVER as a replacement for observed timestamp/venue. Cross-session trading can be continuous as observations, but prices/volumes do not share equal liquidity and executable depth.
- Input observation fields: instrument, timestamp UTC, exchange-local timestamp, source, venue, price/bid/ask, volume and coverage, available_at, ingested_at, TTD, session and normal-session reference close. Do not invent premarket consolidated coverage or quote depth when feed lacks it.
- Session snapshots: decision_as_of, session, completed 1/5/15/30/60m windows, session-to-date high/low/volume/number of actual observations, prior regular close, cross-session change, and missing-bar/completeness verdict. Include boundary snapshot sequence `RTH_close -> AH_last -> PRE_first -> PRE_last -> RTH_first` only if each observation exists; absent boundary fields null. 15-minute peaks represent actual observed high trades, not rounded candle closes; volumes must be provider coverage-verified.
- For overnight gaps identify prior RTH close as anchor; preserve AH end and PRE first separately. "AH high" and "PRE high" are different maxima. No false uninterrupted bars across closed or unobserved periods.
- Unify symbols and observed data through B02 resolver and daily JSONL partitions, preserve session tags and daily file policies. A daily partition must have explicit timezone/calendar key, including crossing UTC midnight. Never silently combine same symbol across disparate venues, corporate actions or currencies.
- Shared macro inputs—ICI flows, money market AUM, Fed reserve/financial condition series, credit indices, yields and treasury settlements—retain publication cadence and timestamp; session requests read the most recent decision-time eligible release, not a fabricated 15m observation. Publication age visible independently of source-domain TTD.

### Session-specific interpretation, without three engines
| Profile | Main emphasis | Additional cautions |
|---|---|---|
| PRE | Overnight gap, AH persistence vs reversal, futures/ETF-sector divergence, expected open catalysts, quote spread/depth | Thin volume, participant selection, stale prints and unreliable breadth |
| RTH | Tradable acceptance/rejection, synchronized index breadth, turnover, liquidity, options/hedging and cross-sector confirmation | Opening/closing auctions, volatility halts, intraday seasonality |
| AH | Earnings/events, RTH close to AH repricing, sustained versus isolated prints, next-PRE reference | Thin depth, limited venue coverage, next-day continuation unproven |

The same deterministic geometry functions should operate with session-scoped parameters. Compare 15-minute volume against same-session and same-clock-time historical distributions, not RTH against PRE raw counts. No predictive regime probabilities unless walk-forward calibrated.

### Interfaces to existing work (read-only dependencies)
- B17 #100 / PR #101: reuse `engines/composites/market_context/context.py` versioned basket/universe, synchronized 5/15/60m context and strict stale/missing evidence controls. B17 owns any eventual modification to this engine in its owning worker, not #163.
- B17 #158 / PR #159: reuse macro delta and physical supply risk research; avoid separate flow archive and "no_new_observation" interpretations.
- B06 #149 / PR #150: reuse `engines/traversal/market_geometry/core.py` 1/5/15/30/60m returns, range position, velocity/acceleration and QQQ/SPY, RSP/SPY, SMH/QQQ, IWM/SPY relatives; B06 owns future function modifications.
- B02 #148, #151 / PR #153: use the canonical entitlement, venue, session calendar and replay/TTD source adapter when it is verified. Never assume available from a PR description.
- B00 to define cross-domain session/output schema; B01 to independently test end-to-end point-in-time replay and source freshness.

### Required acceptance tests by receiving owners
T1: PRE/RTH/AH classification at 04:00, 09:30, 16:00, 20:00 ET and DST, early-close/holiday/session-not-supported cases.
T2: AH-to-PRE and PRE-to-RTH comparisons preserve three separately timestamped anchors and null missing points.
T3: 15m highs/lows and dollar-volume are based on observed bars/trades, with completeness checks and provider venue coverage.
T4: Same-clock-time volume baseline; no RTH liquidity threshold applied to PRE/AH.
T5: Weekly fund-flow observation first available after a decision timestamp is excluded from that report and replay.
T6: Source stale/partial/unknown statuses force unknown classification where critical evidence missing; no manufactured certainty.
T7: Existing B06 geometry outputs and B17 market context remain numerically identical on matched eligible RTH fixtures (non-regression).
T8: Forward session-to-session trading research includes spreads/transaction costs, gap slippage, missed rebounds and distinct unexecutable thin-liquidity scenarios; no fabricated probabilities.

### Proposed user-facing view
`SESSION | as_of | prior RTH close | RTH/AH/PRE high-low-volume + observation coverage | 15m peak and volume | QQQ/SMH/NVDA relative | credit spread delta | MMF/equity/bond last-publication flows | state/supporting/contradicting observations | next falsifier`.
Prefer one tracking conversation with `session=auto|PRE|RTH|AH|all` queries. Conversation UI is a readout, not a data store, durable worker or independent authority.

## Disposition
Research contract complete when this exact file is committed and a draft PR is opened. Implementation, backtesting and production operation explicitly **pending**, not falsely declared complete.


## Deterministic receiver fixtures and decision rules (2026-11-06; specification only)

These are explicit **synthetic test inputs**, not observations, live prices or empirical calibration. Each fixture declares `decision_as_of` and expected outcome; the receiving owner should transcribe the vectors into its own domain tests without altering this B17 document.

### Minimum session algorithm (proposed, subject to B00 calendar governance)
1. Parse each observation as an offset-aware UTC timestamp; resolve its US exchange-local wall-clock date and the applicable session calendar. Reject naive or ambiguous timestamps. Use the venue's eligible coverage; do not infer a consolidated tape from a limited provider.
2. For a **normal full US equity session**, classify times [04:00,09:30) PRE, [09:30,16:00) RTH, [16:00,20:00) AH, otherwise CLOSED. Exactly 09:30 is RTH; exactly 16:00 AH; exactly 20:00 CLOSED. Special calendars, early close, halts and venue/product-specific overnight trading override this default mapping; unsupported windows must not be silently labeled CLOSED if the provider actually supports overnight trading.
3. Compute windows using only completed eligible observed intervals ending at or before `decision_as_of`. A 15m peak means the max observed high over an explicit 15m interval, not merely the last trade or the rounded close; for missing intervals preserve `observed_peak` but set `complete=false` and withhold completeness-dependent comparisons. Partial first/last windows must be marked as partial.
4. Session anchors use calendar-linked previous RTH close, AH latest, next PRE first/latest and subsequent RTH first. Preserve each anchor's timestamp/quality; do not substitute a later session price for a missing prior anchor. Gaps are descriptive differences, not proof of executable tradable returns.
5. All released fundamental/fund-flow inputs must satisfy `first_available_at <= decision_as_of`, provider entitlement and source validity; `ingested_at` must also be visible. For a historical *as-known* replay, enforce `ingested_at <= replay_dataset_cutoff` or use an explicitly frozen vintage. Publication `period_end` alone never establishes availability.
6. Classify a regime only when its required independent source families meet explicit availability and coverage; otherwise `indeterminate` with missing sources. Do not infer that equity inflows are funded by bond redemptions, or that equity turnover is a net flow.

### Synthetic acceptance vectors
| ID | Decision point and inputs (America/New_York unless explicit UTC) | Expected assertion |
|---|---|---|
| S01 | Normal trading day 03:59:59, 04:00:00, 09:29:59, 09:30:00 | CLOSED, PRE, PRE, RTH respectively |
| S02 | Normal trading day 15:59:59, 16:00:00, 19:59:59, 20:00:00 | RTH, AH, AH, CLOSED respectively |
| S03 | 2026-03-06 09:00 ET; 2026-03-09 09:00 ET (after US DST switch) | Both PRE by local exchange wall clock; offset differs -05:00 vs -04:00. Neither is matched to same UTC hour |
| S04 | 2026-11-02 09:00 ET (after autumn DST switch) | PRE at -05:00; use calendar/time-zone conversion, not manually hard-coded UTC offset |
| S05 | NYSE scheduled early-close date, decision at special close time and 15m afterward | RTH ends at the official special close; AH availability/classification depends on venue and approved calendar; expected `unsupported_or_unknown` until configured, not a fabricated normal RTH candle |
| S06 | Saturday 09:30 ET for an ordinary US stock | CLOSED/unsupported; never fabricate RTH session merely from clock time |
| S07 | Last RTH close 200.00; AH last 202.00; next PRE first 201.00; PRE latest 199.00 (synthetic USD) | AH/RTH +1.00%; PRE-first/AH -0.4950%; PRE-latest/prior-RTH -0.50%; separately labeled denominators, timestamps, venue and no interpretation as net order flow |
| S08 | Prior RTH close 200.00; AH observation missing; PRE first 201.00 (synthetic USD) | AH anchor `null`, AH-to-PRE change `null`; PRE-first/prior-RTH +0.50% may be shown as separate comparison |
| S09 | 09:00–09:15 PRE synthetic OHLCV: high 205.00, low 198.00, close 201.00, volume 1000; 09:15–09:30 missing | First observed 15m high 205.00; 09:15–09:30 peak/volume `null`, completeness false; no inferred uninterrupted high or full 30m volume |
| S10 | RTH 15m 1,000,000 shares versus PRE 15m 10,000 shares | No absolute-volume strength comparison without same-clock/session historical baseline and coverage; both raw observations may remain available |
| S11 | ICI report `period_end=2026-10-28`, `first_available_at=2026-11-06T09:00:00-05:00`, decision 2026-11-06T08:45:00-05:00 | Excluded from this PRE report and as-known replay despite older reporting period |
| S12 | Same report as S11 at decision 2026-11-06T09:05:00-05:00 with valid ingest/vintage cutoff and approved TTD | Eligible as latest published weekly context; NOT a freshly measured five-minute flow |
| S13 | Money-market assets +$20B, weekly net MMF subscriptions +$15B, equity fund net flows +$12B (synthetic, non-overlapping) | Show three distinct quantities; do not conclude $20B exited equities or add AUM delta to fund subscriptions |
| S14 | Bond funds+ETFs +$10B, of which bond ETFs +$7B (synthetic same coverage interval) | Bond combined stays +$10B, ETF component shown as subset; NEVER report +$17B |
| S15 | Source quote timestamp 08:00 ET, decision at 09:00 ET, configured quote TTD 60s | Stale price; no current-price claim or current-sensitive classification |
| S16 | One volume provider supplies partial venues; benchmark from consolidated trade volume | Mark incompatible coverage; do not classify unusual 15m volume from incomparable venues |
| S17 | Complete RTH fixture supplied to existing B06 geometry and proposed session adapter | Previously validated B06 return/range/velocity numbers remain identical, within declared numerical tolerance; any change is a regression |
| S18 | Security supports overnight exchange trading outside 04:00–20:00 ET | Do not erase actual observed trades as CLOSED; require new explicit segment definition/owner decision under B00 |

### Quantitative checks independent of empirical alpha
- Formula: `percent_delta = 100 * (new_price / base_price - 1)` only if both positive, same split/FX basis, available and correctly tagged; `null` otherwise.
- Shares and USD notional must stay different units. `notional_usd = sum(price_i * eligible_shares_i)` where an eligible trade stream is available; a minute bar's `close * volume` is an approximation and must be labeled, not reported as true executed notional.
- For 15m time buckets, specify exact `[start,end)` and session membership; use 15m aligned windows local to session start unless a receiving contract explicitly dictates a different anchor.
- Holiday, suspension and unexpectedly empty provider response are three different states: `not_scheduled`, `halted` when independently observed, `missing_source` otherwise.
- Out-of-sample study must compare identical as-of clocks, traded instruments and eligibility, with same costs and missingness accounting. Define improvement targets before testing and preserve null outcomes. Synthetic fixtures validate contract semantics only, not trading performance.

### Cross-owner release checklist
B00: accept or explicitly change calendar, session identity and observation interface in existing shared-contract scope, resolving issues #202/#163.
B02: prove canonical source resolver, entitlement, append-only daily JSONL/session partition and replay semantics on provider-supported real captures.
B06: verify market geometry uses same synchronized observation windows with no duplicated calculations.
B17 owner: integrate shared capital-flow / credit interpretation without adding new price-feed stores or competing market-context engine.
B01: independently validate provider fixtures, expected test vectors, exact-head CI and post-integration main.
Until all gates pass, report `research_spec_only`; no functioning all-session service, reliable 15m monitoring, or measured predictive performance is established.


## Risk-gated market snapshot upgrade — 2026-11-06

Status: **proposed B17 analysis contract, no production source ingestion or live deployment**.

### Real captured example (Massive API one-time snapshot)
2026-11-06T13:35:36Z approximate observed timestamp (per-ticker trade times differ by seconds; retain raw nanosecond `lastTrade_t`). Provider: Massive U.S. stocks full-market ticker snapshot, request universe `NVDA,SMH,QQQ,SPY,CRWV,MSFT,AMZN,GOOGL,ORCL,AAOI`. Representative observed last trades: NVDA 189.5054 (today change +4.3532%), SMH 469.91 (+4.9539%), QQQ 656.79 (+1.5053%), SPY 734.52 (+0.2074%), CRWV 47.5066 (+8.8104%), MSFT 530.32 (-1.0468%), ORCL 119.58 (+3.8381%), AAOI 48.74 (+3.9454%). Values are USD and quote-feed observations, not executions available at the reader's current time. This paragraph is provenance for a one-time research observation, NOT canonical ticker JSONL, permanent market capture or a guarantee of source persistency. Source provider response was retrieved on 2026-11-06. Data availability vs ingestion timestamp in this research report is not a substitute for an entitled durable B02 ingestion record.

Descriptive read: highly positive semiconductor/AI dispersion vs SPY with weaker MSFT; a selective risk-on bid, not confirmed equity-market-wide reversal. Nothing in this snapshot proves bond/money-market net transfers, institutional participation, credit health or persistence after 09:30 ET. Do not convert this illustration into historical inference without preserved provider raw response and as-of timestamp.

### Proposed risk-gate output fields (not yet a shared schema)
- `as_of_utc`, `session_id`, `exchange_calendar_id`, `snapshot_source`, `entitlement`, `market_timestamp`, `first_available_at`, `ingested_at`, `ttd_seconds`, `coverage_status`, `age_seconds`.
- `price_momentum`: synchronized 1/5/15/30/60m returns and session high/low position; source B06 market_geometry, not duplicate calculations.
- `participation`: QQQ/SPY, SMH/QQQ, RSP/SPY, IWM/SPY relative strength; eligible constituents only; missing RSP/IWM => `unknown`, never `breadth_confirmed`.
- `execution_liquidity`: spread/depth/eligible venue coverage and time-of-day expected volume (only if available); if missing, `unknown`.
- `funding_credit`: published HY/IG spreads and trend; SOFR/repo and funding exceptions; last publication effective/available times; missing => `unknown`.
- `fund_allocations`: last public MMF assets+MMF net flows, long-term bond/equity net flows, report period and latest vintage; must not be characterized as tick-by-tick transfers.
- `event_overlay`: scheduled economic releases, earnings, financing events and stale/unknown source categories.
- `interpretation`: independently report `ai_sector_bid`, `broad_market_confirmed`, `credit_confirmed`, `execution_liquidity_confirmed`, each true/false/unknown and supporting/contradicting inputs. If only sector bid confirmed, state `selective_rebound_unconfirmed`.
- `scenario_triggers`: scenario, numeric reference baseline and as-of, what observation confirms/invalidates, without invented probability. The current provider last-trade print is not an order trigger or executable price.

### Decision priority
1. A current and entitled timestamped snapshot is necessary to make any statement about "now". Missing/stale inputs produce `UNKNOWN_CURRENT`, not zero returns.
2. Cross-market confirmation is separate from sector intensity. AI names outperforming does not alone establish broad risk-on. Require explicit QQQ, SPY, RSP and IWM comparable observations and directional rules chosen by B17, validated later.
3. Credit and funding change is separate from market prices and weekly fund-flow publications. If absent, indicate `CREDIT_UNVERIFIED`.
4. Distinguish volatility compression, relief rallies, and trend reversals as different hypotheses; a confirmed reversal requires prespecified persistence and breadth/credit evidence plus historical testing before assigning predictive meaning.
5. Protect against selection bias: for intraday "peak" tracking do not compare PRE highs of liquid stocks with thin AH highs on identical thresholds; preserve actual high touch, window volume, coverage and known first availability.
6. Only score empirically tested signal combinations. The initial rule-based readout emits non-probabilistic states and exposes its data limitations. Validate any forecast against price-only and geometry-only baselines including slippage, false positives, missed reversals and transaction costs.

### Owner-specific implementation sequence
- B02 **capture first**: entitled Massive snapshot/minute adapters, replayable timestamped per-ticker daily JSONL with venue/coverage and TTD, 15m complete windows only on real bars. Source snapshotted results must not be passed off as durable canonical data unless the B02 owner ingests and verifies them. Dependency #148 and separate B02 handoff below.
- B06 **recompute second**: consume canonical B02 observations, no duplicate bar store, independently verify 15m touch prices, volume and relative returns.
- B17 **interpret third**: adapt existing market-context PR #101 with these risk gates after ownership/collision review; no parallel live market scanner and no hardcoded weights.
- B00/B01 **contract/verify last**: B00 #202 mediates shared schema, B01 exact-head independent replay/CI; no merge before user authorization.

### Proposed safety/regression acceptance
R1: A price snapshot with all 10 names but no RSP/IWM and no verified credit input MUST show sector leadership with breadth/credit `unknown`.
R2: Two identical snapshots with different observation ages, one over declared price TTD, MUST differ in admissibility even when price does not change.
R3: A bond inflow published after decision time MUST NOT inform the earlier regime.
R4: Missing 15m minute bars MUST NOT yield an asserted interval peak/full volume.
R5: Repeated ingestion of identical raw trades MUST be idempotent; conflicting corrected values use append-only revision semantics.
R6: Relative-return comparisons require synchronized eligible timestamps and compatible adjusted price scales.
R7: PRE→RTH→AH replay must retain session anchor points and separate condition labels, never collapse separate market sessions into one unqualified "day high".
R8: Any claimed predictive improvement must survive point-in-time out-of-sample ablation versus B06 price geometry and B17 base context. Not run yet.
