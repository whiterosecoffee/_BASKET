# Worker A — Market Vector & New High/Low Tracker (B06 specification)

**Origin:** B06 issue #155, branch `work/155-market-flow-watch-review`. **Design only; not a deployed service.**
**Execution owner:** B06 for range/traversal state and event detector. B02 owns entitled capture/TTD/replay; B17 owns breadth and relative-market context; B01 verifies cross-domain integration; B08 handles delivery. B00 arbitrates shared contracts and dispatch. Never code other sparks' paths.

## Mission / user decision
Track **current market vectors**, new highs and lows, market traversal and reversals; issue **only** meaningful state-transition alerts. The tracked working universe is QQQ, SPY, NVDA, AAPL, MSFT, AMZN, AMD, MU, AVGO, GOOGL, GOOG, META, TSLA, ORCL, CRWV and NDX/SPX/VIX. Extend by ticker registry/subscription, not by hardcoded duplicated adapters. Explicitly distinguish monitoring universe from user-focused entry list (NVDA/CRWV/COHR/MRVL/LITE/INTC/AAOI/CRDO/ALAB).

## Reuse first
- B02 observation journal #11/PR #15 and Massive fetch architecture #151/PR #153.
- B06 multi-range metrics #108/PR #109, synchronized geometry #149/PR #150, October morphology #144/PR #145, self-relative state #154/PR #160 and after-hours MRI #166/PR #168.
- B17 cross-basket market context PR #101; B08 snapshot service PR #55.
Inspect actual current main/PR-head status before reuse. Draft PR is not merged production functionality.

## Minimal read-only input contract (proposal, B00 owns formal shared schema)
For each observation: instrument_id, ticker, venue, asset class, currency, UTC source event_at, provider available_at (null if unavailable), observed_at, ingested_at, exchange session + timezone, data entitlement, provider/source URL, adjusted/raw flag, previous **regular** close, regular/extended close, last-trade and minute-bar price with selection rationale, high/low/VWAP for the matching session, volume (shares / USD turnover), provenance ID, TTD and input manifest digest. Index quotes cannot substitute for contemporaneous after-hours data. Require synchronized cutoff and explicit lag for each instrument. Absence/stale/conflict => `unknown`, never zero change.

## Outputs: one vector_state event, zero or one user notification
- Separate prior-close return (%) and same-session prior-snapshot return (%); specify windows. Include QQQ minus SPY return in percentage points; NDX minus SPX likewise.
- Completed 1/5/15/30/60m and current-session high/low/new high/new low, distance to prior session low/high and rolling 5/20/60/200 **completed-session** extremes, with timestamp and adjusted-basis consistency.
- Range location, price displacement per 1M shares and per $1B executed turnover (descriptive only), net displacement vs summed absolute path (efficiency), trade count, share turnover, optional same-clock 20-session RVOL when available; if baseline missing => null. No claim of net aggressive buying from OHLCV.
- Sector: 4-name semiconductor breadth (NVDA, AMD, MU, AVGO), 5 major platform firms including AAPL/MSFT/AMZN/GOOG or GOOGL/META (avoid double counting Alphabet share classes), optional issuer market-cap weights only if dated and verified.
- VIX current only when contemporaneous and session-valid; material rate/spread overlays if source-verified.
- Observed state: `unknown|balanced|recovery_attempt|confirmed_recovery|failed_rebound|downside_extension|liquidation_stress`, with evidence, event time, prior state, trigger, invalidation, confidence *category of evidence completeness*, and versioned detector/config.

## Event rules
Freeze thresholds prospectively (per instrument/session); B06 to calibrate from historical replay before publishing numerical thresholds. A single VWAP touch, low print, or HIRO reading cannot certify a regime change. Use completed bars, minimum contact and persistence windows, hysteresis, event journaling and dedupe episode IDs. New highs/lows are **observations**, not necessarily alertable; alert only when accompanied by qualifying participation and confirmed transition. Distinguish 52-week, rolling sessions and current session; no look-ahead. No repetitive unchanged-state messages. Closed sessions silent except material after-hours event or independently verified operational incident.

## First slice (smallest useful)
1. Read-only adapter consuming a frozen B02 observation fixture; no ingestion rewrite.
2. Deterministic per-ticker extremes, 5/15/30m percentage vectors, range position, VWAP distance and evidence freshness.
3. QQQ/SPY and semiconductor breadth on one aligned cutoff; no invented weights.
4. Pure event-state transition with explicit unknown/null and no-event output.
5. Output a concise human summary and machine-readable JSON fixture; no delivery service initially.

## Acceptance tests (B06 domain + B01 integration)
- Split/adjusted prior close; daylight-saving/early closes/holidays; premarket vs regular vs after-hours.
- Repeated equal highs/lows, corrected late minute bars, stale index at after-hours, contradictory last-trade vs minute-bar, missing volume, missing prior snapshot.
- % return vs percentage-point return; 5/15/30m path and turnover math; 20-session RVOL null if incomplete.
- Event dedupe, hysteresis, resolved/superseded event, no notification on no change, historic replay of Nov 2–4 with timestamp-consistent verified inputs (not transcript assertions alone).
- Component tests on exact commit and B01 independent exact-head checks. Never claim empirically useful thresholds without walk-forward labels/calibration.

**Dependencies / permitted code paths:** B06 `engines/traversal/**` only after collision review. B02 `runtime/**` / `tickers/*/intraday/**`, B17 `engines/composites/**`, B01 `tests/integration/**`, B08 `services/**`. This planning document alone confers no cross-domain write permission.
