# AH-MRI — after-hours market regime intelligence (research contract v0.2)

Spark B06 | worker issue #166 | branch `work/166-ah-market-regime-intelligence` | **research-only; not a deployed service**.

## Purpose
At a specified point-in-time, produce a concise USD-first close/AH report, market state, observed candidate support zones and conditional stress paths for the next relevant session. Always state **which session** the price belongs to, source and freshness. Explicitly separate observation, technical inference, conditional scenario and unknown. A "floor" never implies guaranteed support.

## Scope and reuse
This folder is uniquely owned by #166. Reuse but do not copy existing B06 range engine #108/PR109, synchronized 1/5/15/30/60m market geometry #149/PR150, historical compression #144/PR145 and SMA30 experiment #154/PR160. Consume B17 market-context #100/PR101 for breadth/relative leadership. B02 owns entitled data ingestion, session calendars, snapshot provenance, FX and TTD; B00 owns shared schemas/architecture; B01 owns cross-domain CI. The proposed interface is NOT a new shared schema. Never assume unmerged PR features are on main.

## Sessions and schedule
- regular session: NYSE/Nasdaq calendar, prior **completed** trading day 09:30-16:00 America/New_York, with exchange holidays and early closes;
- AH: 16:00-20:00 local exchange time **only where provider actually reports an eligible trade**; distinguish quote, last trade, regular close, extended-hours volume. Do not silently combine fragmented after-hours prints with consolidated RTH OHLCV;
- next release: identify official scheduled economic events and earnings with source links, consensus timestamp, release timestamp/time zone. A scheduled event is not an observation.
- snapshot identity: `as_of`, `session_date`, `venue`, `session_type`, `provider`, `source_class`, `effective_at`, `observed_at`, `available_at`, `ingested_at`, `expires_at`, `input_manifest_hash`, `engine_version`, `git_sha`. Leave absent timestamps null. Expired observations remain historical, NEVER live. Store immutable revisions/ids in B02 canonical store only.

## Candidate floor evidence hierarchy (strongest to weakest, conditional on coverage)
1. Measured volume-at-price acceptance with verified price/size and consistent adjustment basis, multiple touches/rejections and bounded completed sessions.
2. Verified anchored VWAP and prior high-volume price area/retest + session-specific range endpoints.
3. Volatility-normalized historical support/resistance and cross-market confirmation.
4. Independent options strike concentration, put/call OI, dealer **signed** gamma estimate with contract multiplier, expiration, underlying and volatility assumptions; OI alone cannot establish dealer net positioning.
5. Pure round-number/previous intraday low = **reference**, not confirmed floor.

Each zone must have `kind` (observed/reference/scenario), `lower_usd`, `upper_usd`, `calculation`, `evidence_ids`, `sample_window`, `data_gaps`, `confirmation`, `invalidation`, `status`, and `confidence_class` (measured/qualified/unverified; NOT a probability). Reject unnamed precision. A downside stress zone derived from assumed percentage move must be labeled `scenario`, not observed support.

## Event surprise and stress
Compute economic surprise only when `actual` and point-in-time `consensus` have identical defined units and publication/revision vintage. `surprise = actual - consensus`; separately classify economic meaning and equity-market sign, since stronger growth can offset hotter inflation. Keep release-time windows 0-5, 5-30, 30-60 minutes and close for validation when observed bars are contiguous; exclude pre-release and unavailable quotes. Rate and equity comovement is descriptive; attribution requires explicit alternatives. Compare Treasury 2y/10y, credit HYG/LQD (proxies, not company credit spreads), QQQ/SPY, RSP/SPY, IWM/SPY, SMH/QQQ, NVDA, AVGO, MSFT, AMZN, GOOG/GOOGL, META, AAPL, CRWV, ORCL; oil/USO, VIX and USD where entitled data are available. Missing series remain missing.

Three independent next-session hypotheses:
- absorption: primary zone tested, hold/reclaim on volume and breadth; invalidated by sustained acceptance below;
- continuation: confirmed loss, failed retest, negative breadth/relative strength; invalidated by durable reclaim;
- dislocation: gap through multiple zones with widening ranges, credit/rates stress and trading-liquidity impairment; invalidated by normalized ranges and recovered participation.
These are conditional descriptions, not calibrated likelihoods, price targets or financial advice.

## Required report order
1. **As of / market session / evidence freshness** and 1-sentence bottom line.
2. Five-column cross-asset board: instrument, regular close, RTH % move, AH mark/time (if valid), interpretation.
3. Leadership/breadth/sector concentration and volatility regime.
4. Event calendar (release, consensus vintage, "adverse" definitions and mechanism).
5. **Downside battle bands** for SPY, QQQ, NVDA and other user-selected names: first reference, confirmed measured zone, deeper stress scenario; zones may be null.
6. Conditional trigger/invalidation table; overnight futures/foreign session where comparable.
7. Unknowns, contradictions, data gaps and next measurement; NEVER claim monitoring unless scheduler/runtime is confirmed operational.

## Quality gates
- Same-symbol all values same adjustment/venue convention; no timestamp after `as_of`.
- No quote overwrites closing auction or cross-session market high/low.
- No "confirmed support" without at least documented repeated defense or price/volume acceptance; insufficient coverage -> null.
- No fabricated gamma, flow, probabilities, implied market-maker inventory or interpolated options surfaces.
- Detect adverse data versus expectations; "negative" must specify inflation, growth, liquidity or earnings.
- Historical June 24, 2026 prices/floors stated earlier in the conversation are illustrative UNVERIFIED material; not used as fixtures, not current Nov 2026 levels.
- Replay at past `as_of` must exclude late revisions and compare detected zone breach/hold against subsequent data with explicitly defined horizon/costs. Test hold/fail rates out-of-sample before translating into percentages.
- Output should be auditable and concise; no order placement.

## Sources and prior-art families
- **Auction/market profile and volume-at-price**: acceptance/rejection and liquidity zones; the exact vendor profile implementation needs disclosed trade/quote coverage.
- **Technical analysis and volatility normalization**: Wilder ATR, moving-average confluence, VWAP/anchored VWAP, historical pivot zones. Indicators are fallible summaries.
- **Macro event-study and high-frequency identification**: Federal Reserve Bank of NY, *How Economic News Moves Markets* (2008), https://www.newyorkfed.org/newsevents/news/research/2008/rp080908 ; San Francisco Fed US Monetary Policy Event-Study Database (updated 2026-10-30), https://www.frbsf.org/research-and-insights/data-and-indicators/us-monetary-policy-event-study-database/ ; Kansas City Fed (2025), https://www.kansascityfed.org/research/economic-review/estimating-the-effects-of-monetary-policy-an-ongoing-evolution/
- **Macro-factor and regime approaches**: independent breadth, Treasury, credit, volatility and sector channels, avoiding ex-post causal certainty.
- **Derivative market microstructure**: option OI vs signed dealer gamma and hedging uncertainty; signed inventory must never be inferred from strike OI alone.
- **Risk/scenario analysis**: conditional path/stress testing with falsifiers rather than invented likelihoods.
- **Point-in-time quant research and event sourcing**: immutable observation vintages, walk-forward tests, survivorship/availability and data leakage checks.

## Status
Runnable offline research prototype (core.py, readiness.py and run.py), with 20 synthetic regression cases defined in test_core.py and test_readiness.py. The canonical source adapter, production runtime, source-backed support detector, real market replay, confidence calibration and independent exact-head CI remain external dependencies. The prototype does not generate verified market data. See CONTRACT.json, RUNBOOK.md and ACCEPTANCE.md.
