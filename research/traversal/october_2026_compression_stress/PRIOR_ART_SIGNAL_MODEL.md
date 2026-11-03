# Prior art for multi-scale market chop, directional traversal and liquidity resistance

Research note for B06 issue #144 / draft PR #145. Concept exploration; not implemented or calibrated.

## Core reframing
Not merely 'tracking chop at scale' but multi-clock price-discovery and liquidity traversal. Preserve independent state dimensions: signed direction, normalized velocity/acceleration, path efficiency/chop, participation intensity, liquidity/impact, nested range position, structural persistence, and market/peer residual. A flat or slowing net return is not proof of absorption; two-way activity, trade-sign, depth, auctions and temporary price impact can explain it.

## Prior-art map (reference / downstream function)
1. Cont, Kukanov, Stoikov (2014) *Price Impact of Order Book Events*, DOI 10.1093/jjfinec/nbt003: order-flow imbalance and inverse depth; authoritative for book-based resistance. Requires entitled trades+quotes/book; OHLCV proxy must remain labeled.
2. Hasbrouck (1991) *Measuring the Information Content of Stock Trades*, DOI 10.1111/j.1540-6261.1991.tb03749.x: distinguish temporary vs persistent price impact and lagged price adjustment; track post-contact decay over defined follow-up horizons.
3. Perry Kaufman efficiency ratio (e.g., *Smarter Trading*, 1995): |net price change| / sum absolute increments. Paired with signed move and realized path; low ratio is chop not necessarily absorption.
4. Volume / dollar / imbalance bars, VPIN literature: event-time rather than clock-only; compare activity required to traverse a fixed band. Ke & Lin (2017), DOI 10.1561/104.00000046 and *VPIN and the flash crash* stress trade classification sensitivity. Avoid false 'informed probability' claim.
5. Market/volume profile and auction-market theory: boundaries, accepted/contested prices, test duration and repeat touch; exact volume at price requires ticks, minute VWAP buckets are approximations.
6. Kyle/Amihud impact proxies: price change relative to signed imbalance / volume; 'bps per $1B' is descriptive turnover efficiency, not identified causal impact; cross-asset compare using same-clock own-history z/percentiles.
7. Bayesian online change-point / CUSUM: detect shifts in local mean/variance/order-flow regime using prefix-only updates, not full-sample retrospective segmentation. Tsaknaki et al. (2024), DOI 10.1080/14697688.2024.2337300.
8. Mandelbrot, Fisher, Calvet (1997) *A Multifractal Model of Asset Returns*, Yale Cowles DP 1164: different scaling laws for returns and volatility; verify that a micro-reversal is not falsely treated as reversal of 60m/20d parent trend.
9. High-frequency realized variation and jump/noise methods: distinguish intrawindow gross path from directional displacement, measurement noise and jump effects; https://doi.org/10.3868/s060-011-020-0007-1.
10. Event sourcing, bitemporal data, interval/overlap graph: immutable range creation, contact, defended low, breach, reversal candidate and outcome; no hindsight mutation, multiple parents and overlapping intervals.

## Measurement vector per fixed window
`signed_bp=10000 ln(P_end/P_start)`;
`velocity_bp_per_min=signed_bp/minutes`;
`gross_path_bp=sum abs(10000 ln(P_i/P_{i-1}))`;
`path_efficiency=abs(signed_bp)/gross_path_bp` when denominator nonzero;
`turnover_usd=sum volume_i*VWAP_i`;
`turnover_intensity=(turnover_usd/minute)/(median same-clock USD/minute prior eligible sessions)`;
`turnover_efficiency=signed_bp/(turnover_usd/1e9)`;
`flow_imbalance` and `depth` null without entitled trade/quote data;
`impact_persistence` measured after event across frozen horizons;
`boundary_persistence`: tested, rejected, breached, recovered over time, with all event times;
`peer_residual_bp` relative to predeclared benchmark beta, as-of.

Compare clock-time bars, equal-notional bars and predeclared volatility-adjusted directional-change events with no double counting of overlapping observations. Normalize notional by own-history same-clock and peer liquidity; do not equate $1B in QQQ with $1B in AAOI. Price path efficiency low does not determine direction or resistance.

## Signal state as a vector rather than one score
- `direction`: up/down/flat and signed evidence
- `path`: efficient/choppy and denominator quality
- `pressure`: aggression imbalance when observable; otherwise unknown
- `liquidity`: impact/depth with quality provenance
- `structure`: range test, defense, failure, breakout, unresolved
- `scale`: micro, session, multi-session, macro; may conflict
- `context`: peer-relative vs common-factor movement

Example: 'micro defense candidate inside active 20-day downtrend; rising same-clock turnover; declining net downside impact; low path efficiency; aggression unknown; not a reversal'.

## Falsification
Track all candidates including failures, compare alternative price-only/ATR/VWAP/volume baselines, no threshold tuning on November 2 after examination. Walk-forward with as-of input snapshots, data availability and auction exclusion. Report false positives, detection delay, canceled attempts, censored outcomes, missing rebound cost, turnover/spread costs and sector/macro controls. No predictive probabilities until B07 calibration.

## UI
Show aligned views: price versus historical battle boundaries, cumulative dollar activity, path-efficiency/impact, and nested regime timeline; never mistake diagram for evidence. Each battle click returns full append-only JSONL provenance and event ancestry. Separate primitive observed measures from inference and classification.

Sources:
https://academic.oup.com/jfec/article-abstract/12/1/47/816163
https://doi.org/10.1111/j.1540-6261.1991.tb03749.x
https://doi.org/10.1561/104.00000046
https://www.sciencedirect.com/science/article/pii/S1386418113000189
https://www.tandfonline.com/doi/full/10.1080/14697688.2024.2337300
https://cowles.yale.edu/node/145456
