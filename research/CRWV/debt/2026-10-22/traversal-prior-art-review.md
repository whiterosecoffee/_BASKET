# Prior-art review: range traversal, resistance and trading flow
Date: 2026-10-28. B10 #68 / draft PR #69. Source review plus explicitly proposed engineering choices. No new live market conclusion or calibrated trading probability.
This review supersedes any interpretation of our up/down efficiency ratio as a complete traversal model.

## Main finding
A range tool needs separate state, activity and outcome dimensions. A single 1-centered efficiency score describes directional movement per gross turnover but cannot establish signed demand, repeated resistance rejection, acceptance, full-range traversal probability or execution profitability.
Latest user correction is essential: lower drift with no observed ceiling approach must not be described as another ceiling rejection. An old ceiling remains a reference; no new test means no new evidence of defense there.

## Prior-art families and changes
### 1. Return-to-volume / Amihud illiquidity
Amihud uses absolute return divided by dollar volume; NYU V-Lab explains the interpretation as lower liquidity when a given volume accompanies greater return [1].
Our price-travel/turnover statistic belongs to this descriptive family. It is not a newly established causal market-impact law.
Practice: preserve the 1-centered directional ratio as an efficiency diagnostic; show both side numerators/denominators, sample size and neutral turnover. Range width and common daily-volume normalization cancel from the ratio, so keep range position and participation separately.
Test whether it adds information beyond net return, realized volatility, spread and time of day. Use consistent sampling and exclude overnight return from regular-session turnover comparisons.

### 2. Order-flow imbalance, queue imbalance and liquidity resilience
Cont/Kukanov/Stoikov find short-interval price changes related to best-quote order-flow imbalance and depth; their trade-volume relation is noisier [2]. Gould/Bonart investigate bid/ask queue imbalance for one-tick direction, with different results for large- and small-tick stocks [3].
Practice: distinguish executed aggressive flow, resting displayed depth, additions/cancellations and subsequent price response. If entitled synchronized quotes/trades arrive, use midquote returns to reduce bid/ask bounce and estimate depth/refill/OFI. Do not call candle-direction volume buying or selling dollars.
Queue-imbalance results over one tick do not validate 15-minute range predictions. Displayed orders can cancel; do not call a static book screenshot an executable support guarantee. No OFI computed in this prototype.

### 3. Volume-at-price / auction-profile tools
Sierra Chart documents the difference between tick-level actual volume-at-price and approximations made from larger bar records [4].
Practice: exact band-dollar activity requires trade prints with price and size. Our whole-bar VWAP membership is a research approximation and must retain that label. A high-volume node identifies substantial historical trading, not guaranteed buying support or a ceiling; dwell time and trade response determine the inference.
Do not allocate a minute's entire volume to its final price and call it a genuine volume cluster. Do not assume minute OHLC supplies the sequence of within-minute crossings.

### 4. Support/resistance and clustered conditional orders
Osler studies stop-loss and take-profit orders at an FX bank, finding clustering around round prices and a mechanism for both reversals near levels and acceleration after crossing [5].
Practice: resistance may involve executed supply, while a crossing may trigger stops and accelerate travel. Neither occurs simply because a round number was named.
Build prospectively frozen zone versions; count debounced approaches, contact, retreat, crossing and subsequent occupancy as different events. Preserve original zone and create a successor rather than redrawing history.
Evidence comes from FX data and cannot establish the same probabilities for CRWV. Treat transfer to equities as a hypothesis requiring validation.

### 5. Path efficiency / trend-versus-chop
Kaufman's efficiency ratio compares absolute endpoint movement with accumulated absolute movement [6].
Practice: add signed net/path efficiency Q=(last-first)/sum(abs(step)), in [-1,1] on a consistent path, alongside the existing 1-centered score S. Q=0 indicates no retained endpoint progress despite travel; +1/-1 indicates a monotone observed path.
This prevents repeated tiny reversals from being presented as successful traversal. Q still does not identify order aggression or prove mean reversion will continue.
Implemented in v1.1.0 on observed close path; gaps produce null. A close-based path misses intrabar travel; tick/midquote paths require separate sampling/version.

### 6. Nonlinear impact and execution
Zarinelli/Treccani/Farmer/Lillo study institutional metaorders and impact as a function of order size, participation and duration; a universal square-root extrapolation is inadequate across their full sample [7].
Practice: do not extrapolate an observed cents-per-$10M statistic linearly to an arbitrarily large future buy or sale. Gross market volume is not the size of one investor's directional metaorder.
Assess traversal opportunity net of spread, fees, slippage, queue/fill risk and missed rebounds. A 25-cent observed swing is not necessarily a realizable 25-cent round trip. Do not count rebound after a sell as guaranteed re-entry.

### 7. First-passage / barrier-event outcome labeling
The labeling framework in Lopez de Prado's Advances in Financial Machine Learning distinguishes price barriers and time limits; publisher chapter contents identify dynamic thresholds, triple barriers and overlapping sample issues [8].
Proposed application: on each prospectively defined starting event, record whether the upper target or lower failure boundary is reached first before timeout. Store elapsed time, turnover, excursions and censoring.
Timeout is a separate outcome; a still-open episode is right-censored, not a failed traversal. If both boundaries occur in one OHLC bar, ordering is ambiguous without finer data and must not be guessed.
Use state/position, participation, path efficiency and S as features. Outcome probabilities belong to a separately calibrated model; S=1.8 is not an 80% chance or 1.8 probability. Outcome labels/first-passage engine not implemented here.

### 8. Validation, multiple testing and regime dependence
Bailey/Borwein/Lopez de Prado/Zhu formalize the risk that configurations chosen for in-sample performance underperform out of sample [9].
Practice: lock defaults before testing, record all tried windows/band widths/half-lives, use time-ordered held-out sessions and tickers, handle overlapping outcome intervals and report spread/slippage results. Bootstrap uncertainty in session/event blocks instead of treating every neighboring candle as an independent trial.
Compare against position-only, time-of-day, simple net-return and no-trade baselines. Test stability across tick size, liquidity, volatility and trend/chop regimes.
Same-time RVOL must use prior comparable clock intervals, not a linear fraction of ADV. ADV is a scale; participation is a time-conditioned comparison. Current fixture lacks the latter and leaves it null.

## Refined measurement stack
1. State: immutable zone, position, directional drift, current/previous boundary contacts and elapsed time since contact.
2. Effort: gross shares/$, same-time RVOL, spread/depth/OFI only if observed.
3. Progress: S(up/down movement-per-turnover), signed path efficiency Q, net range displacement and full leg completion.
4. Boundary response: approach, contact, rejection after an actual test, crossing, dwell/occupancy, retest and failure.
5. Outcome: target before failure before timeout; duration, turnover, excursions and execution-adjusted payoff.
No scalar score should silently combine all five.

## Vocabulary rule prompted by the user's correction
- 'Drifting lower; ceiling untested': negative displacement and no observed contact with the defined ceiling in the window.
- 'Rejection': an actual defined approach/contact followed by a specified retreat. This requires an event definition and ordering.
- 'Lower acceptance': repeated occupancy below a prior band, not merely a lower single print.
- 'Fading participation': same-time-adjusted activity is falling; raw lunchtime decline alone is inadequate.
- 'Absorption candidate': significant executed pressure with diminishing price response. Without signed data, keep candidate/uncertainty wording.
No-contact does not prove no hidden interest; it says there is no observed ceiling test.

## What changed in practice now
battle_matrix.py v1.1.0 adds signed path efficiency/gross travel, ceiling contact-bar counts, elapsed time since the last contact within the window, debounced close-entry episodes, left-censoring flag and close occupancy above the upper band.
These are descriptive fields, not an independently calibrated rejection/acceptance state machine.
Contact bars are explicitly not independent tests. The default 5%-of-range entry hysteresis is an engineering placeholder, not established optimal prior art.
The 1-centered score formula is unchanged. Historical v1.0 outputs are retained; new v1.1 outputs/history revisions have method hashes.
Nineteen local tests pass, including new straight-path, round-trip, falling-path, missing-bar, no-contact and debouncing cases. Unit tests establish behavior, not predictive edge.

## Next implementation priorities
B06: event-driven zone lifecycle, prospective clustering, complete leg/first-passage records and 'untested ceiling' classification.
B02: timely entitled trades/quotes, consistent bars, same-time volume profiles and corporate-action/session normalization.
B07: sampling sensitivity, calibration/uncertainty and held-out evaluation.
B08: durable single-writer execution/history/rendering; B01: independent exact-head CI.
Reuse #70 rather than create another overlapping shared traversal dependency. No shared-domain edits or live-worker deployment are claimed.

## Primary sources
[1] NYU V-Lab, Historical Illiquidity: https://vlab.stern.nyu.edu/docs/liquidity/ILLIQ-HIST
[2] Cont, Kukanov, Stoikov, The Price Impact of Order Book Events: https://arxiv.org/abs/1011.6402
[3] Gould, Bonart, Queue Imbalance as a One-Tick-Ahead Price Predictor: https://arxiv.org/abs/1512.03492
[4] Sierra Chart, Volume by Price / Volume at Price Calculations: https://www.sierrachart.com/index.php?ID=141&Name=Volume_by_Price&l=doc/StudiesReference.php
[5] Osler, NY Fed Staff Report 125: https://www.newyorkfed.org/research/staff_reports/sr125.html
[6] Perry Kaufman, Matching the Markets to the Strategy: https://kaufmansignals.com/matching-the-markets-to-the-strategy/
[7] Zarinelli et al., Beyond the square root: https://arxiv.org/abs/1412.2152
[8] Lopez de Prado, Advances in Financial Machine Learning, Chapter 3 (publisher): https://www.oreilly.com/library/view/advances-in-financial/9781119482086/c03.xhtml
[9] Bailey et al., The Probability of Backtest Overfitting: https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf

