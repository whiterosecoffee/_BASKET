# ORCL Range Traversal: analysis instructions (today / 72 hours / 10 days)

Status: v0 (unverified, unrun, untested, unmeasured). Issue #81. Reusable for any TARGET ticker by swapping the params; shipped for ORCL.
Partition logic: this folder holds only the traversal vector. Valuation, financing, partnerships and catalysts belong to other vectors and owners (see #76). One window set, one output contract.
Aligned to: tracker panels `traversal` and `market` in `orchestration/ticker_trackers/orcl.json` (#75/#77); baseline engine `engines/traversal/range.py`.

## PARAMS
- TARGET = ORCL
- BENCHMARKS = QQQ, NVDA, IBM, HYG, IEF, USO (same set as the tracker)
- TIMEZONE = America/New_York; CURRENCY = USD
- SESSIONS = regular session only for band construction; extended hours reported separately, never merged

## STEP 0: FRESHNESS GATE (blocks everything else)
1. State first which markets are open, closed or on holiday now, and the current session phase for TARGET.
2. Source priority: (a) repo stores `tickers/<TARGET>/history.jsonl` and `intraday/<date>.5m.jsonl` (owned by B02); (b) the entitled Massive connector with the same endpoint and adjustment basis; (c) anything else is NON-ACTIONABLE.
3. Do not use web quotes for narrow intraday bands.
4. For every input print: source, endpoint, adjustment basis, feed delay, latest bar timestamp, data age, TTD.
5. If `tickers/ORCL/` is absent (true on main today; B02 #61/#62 own ingestion), say so at the top and use Massive only if it returns entitled, timestamped bars. Otherwise stop and report the gap. Never fill missing bars.
6. Proposed TTDs (heuristic, v0): session window = 300 s while open (tracker `traversal` max age); after the close it is historical truth until the next session's first bar. 72h and 10d windows = recompute when a new session's first bar arrives. TTD-expired data is historical, not current.

## STEP 1: WINDOWS (build all three from the same bar set)
Bars: 5-minute regular-session bars (78 per full session) for bands; daily bars for the 10d context and cross-check.

- TODAY: the current regular session from the open to the latest bar. Mark it partial if the session is open. Half-days: report actual bar count.
- 72H: trailing 72 clock hours ending at the latest bar, keeping only regular-session bars inside it. Report the number of sessions covered and any weekend or holiday gap. On a Monday afternoon, 72 clock hours reaches back to Friday afternoon, so it holds part of Friday plus Monday and nothing for the weekend; do not pad closed time.
- 10D: trailing 10 completed trading sessions plus today if open, shown separately. Use daily bars for endpoints and 5-minute bars for touches. If the user means 10 calendar days, say so and rebuild.

For each window print: first and last bar timestamp, bars used, bars missing versus the session calendar, session count.

## STEP 2: PER-WINDOW TRAVERSAL (same procedure, each window independently)
1. Range: high, low, midpoint, last close, position in range = (last - low) / (high - low), return from the prior close. Reproduce `range.py` outputs for the daily series where the repo data exists.
2. Narrow touch bands: find price zones touched repeatedly. Band width is a method parameter; v0 default is 0.25 times the median 5-minute true range over the window. Print the method and version with every band.
3. Distinct touches: an excursion counts once; price must exit the band and reset before the next touch is counted.
4. Per band, report: lower and upper endpoint in USD, pivot, distinct touches, last touch time, rejection distance in USD (the move away after each touch), dwell seconds, break and retest status, invalidation level.
5. Volume per band: label the method. Sum of price times size is exact and needs tick data. Bar VWAP times volume is a bar aggregate. Close times volume is an estimate only. Volume of bars touching a band is not exact volume inside it, and overlapping bands are not additive.
6. Regime for the window: balance, trend_up, trend_down, expansion, event_dislocation or unknown. Never force a chop label. Use unknown when evidence is insufficient.
7. Rank bands by dollar volume, then by distinct touches.

## STEP 3: CROSS-WINDOW TRAVERSAL (the point of three windows)
1. Nesting: is TODAY's range inside, at the edge of, or outside the 72H range, and 72H inside 10D? Print the three positions side by side.
2. Confluence: bands overlapping in two or more windows are merged with a note listing which windows contribute. Do not add their volumes.
3. Conflict: if regimes differ across windows, report the conflict and which window the latest bar sits closest to the edge of. Do not average regimes.
4. Transition events: break from TODAY's band that is a retest of a 72H or 10D band is the highest-information event; flag it.
5. Event dislocation: mark windows containing an earnings print, guidance, financing or partnership announcement (B03 events if present). Report the traversal with and without the event bars.

## STEP 4: DIVERGENCE OVERLAY (secondary, same three windows)
- For each benchmark, compute the window return and a trailing-standardized delta versus TARGET. Align timestamps and sessions; use only information available at each bar (no lookahead).
- A missing benchmark suppresses its comparison. Do not silently reweight.
- HYG and IEF carry credit and rates context; USO is a futures-based proxy.

## STEP 5: OUTPUT (narrow lists, no wide tables)
1. Bottom line: one line on where TARGET sits across TODAY, 72H and 10D, and the single most important band.
2. Per window, three lines max: range and position, top band with dollar volume method, regime.
3. Cross-window: nesting, confluence, conflict, transition events.
4. Ranked scenarios (base, bull, bear) with the USD levels that move each. No probabilities.
5. Decision ladder: if price holds above X then Y, if it breaks X then Z, with invalidation levels from Step 2.
6. Data age, TTD, gaps, assumptions. Final line: "Next step: <queued action>".

## STEP 6: PROHIBITIONS
- No price, volume or consensus asserted without a timestamped source. No forecast probability, no price target.
- Separate verified facts, issuer claims, hypotheses and missing evidence.
- No extended-hours bars inside bands unless reported as a separate set.
- Do not describe the three windows as independent confirmation of each other: they share bars.

## TEST CASES (for the first dry run and for B06 when it implements this)
- Opening-range floor versus repeated support (a first-bar low is not a support band)
- Overlapping touched-bar volumes counted once
- Breakout then retest classified as break_retest, not a new band
- Event dislocation window with and without the event bars
- Monday 72H window spanning a weekend gap
- Half-day or holiday inside the 10D window
- Stale latest bar: output must be labeled NON-ACTIONABLE

## OPEN PARAMETERS (ghost nodes, not next)
- Band width multiplier (0.25 times median true range) is uncalibrated.
- Whether 72H should mean three sessions rather than 72 clock hours.
- Whether 10D should default to calendar days.
- Dwell threshold for a valid band.
- Handoff to B06 for an executable implementation behind the `traversal` panel.
