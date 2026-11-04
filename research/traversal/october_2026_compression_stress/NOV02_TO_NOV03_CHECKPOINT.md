# Nov 2 -> Nov 3 pre-open battle-range checkpoint

Research-only historical/provisional test, not trained prediction. Captured on Nov 3 approximately 09:29 ET using Massive 1-minute completed interval aggregates. **No Nov 3 RTH data yet at scoring cutoff**. Nov 3 premarket kept separate, never added to Nov 2 price efficiency or turnover. Source availability may be delayed; source ingestion/checkpoint environment not a deployed continuous feed.

## November 2 RTH observations
Window 09:30–16:00 America/New_York (14:30–21:00 UTC), final minute stamped 20:59 UTC. Notional Σ(v × vw), not signed capital flow.
| Instrument | RTH low | final 1m close | Last 2h open | Last 2h return | Last 2h notional USD B | Final 30m notional USD B | RTH notional USD B |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QQQ | 680.33 | 681.13 | 688.49 | -1.07% | 13.76 | 4.84 | 32.72 |
| SPY | 751.60 | 752.12 | 757.12 | -0.66% | 17.17 | 9.01 | 32.93 |
| SMH | 506.44 | 508.07 | 515.63 | -1.47% | 1.82 | 0.87 | 4.11 |
| NVDA | 201.66 | 202.20 | 205.49 | -1.60% | 6.63 | 3.12 | 17.92 |
| AMD | 466.0717 | 466.74 | 477.825 | -2.32% | 4.99 | 2.17 | 13.26 |
| ORCL | 118.43 | 119.12 | 121.355 | -1.84% | 2.28 | 1.10 | 5.94 |
| CRWV | 49.46 | 50.16 | 51.51 | -2.62% | 0.83 | 0.29 | 2.20 |
| AAOI | 61.88 | 62.46 | 63.185 | -1.15% | 0.26 | 0.10 | 0.80 |

All eight established RTH session lows inside the final two hours. The approximate 2h return here = final minute close / first minute open -1; official close may differ owing to auction. Note potential SMH minute high spike $524.47 during last 30m despite much lower contemporaneous prices: pending outlier/auction constituent validity check. Do not infer range touch from unvalidated single high.

Final 30m notional concentration vs full RTH: QQQ ~14.8%, SPY ~27.4%, SMH ~21.2%, NVDA ~17.4%, AMD ~16.4%, ORCL ~18.5%, CRWV ~13.2%, AAOI ~12.5%. This is not time-of-day-normalized excess participation; same-clock multi-day reference required.

## Nov 3 09:29 ET premarket checkpoint (separate session)
| Instrument | premarket last minute close | vs Nov 2 official close | Nov 2 RTH high |
| --- | ---: | ---: | ---: |
| QQQ | 684.43 | +0.49% | 699.43 |
| SMH | 520.49 | +2.40% | 532.76 |
| NVDA | 208.00 | +2.94% | 209.9769 |
| ORCL | 122.00 | +2.33% | 126.50 |
| CRWV | 50.83 | +1.36% | 55.738 |
| AMD | 479.98 | +2.81% | 512.82 |
| AAOI | 64.03 | +2.45% | 71.575 |
| SPY | 752.72 | +0.08% | 763.86 |

These extended-hours values are an exploratory contrast; PM trade density and participation are not equivalent to RTH. The preliminary early opening minute, if available later, cannot be scored as a completed 5m confirmation without finishing the window.

## Signal test
- Monday RTH **direction**: down on all eight last 2h; all new session lows late -> high confidence descriptive downward traversal.
- **participation**: significant notional exchanged, but no same-clock prior-day baseline or signed OFI -> cannot label abnormal aggressive seller flow; low confidence participation classification.
- **resistance/absorption**: candidate impact decay and failed temporary rebound recognized in earlier QQQ/NVDA/ORCL replay; predeclared zone/no-lookahead replay still needed. Labels provisional, not universal across eight.
- **Nov 3 premarket**: rebound in all eight, but no RTH higher-low / reclaim / sustained bid confirmed as of cutoff. Do not score overnight recovery as proof October compression regime ended.
- **follow-up frozen test**: evaluate Nov 3 completed 09:30–10:00 and 10:00–11:00 ET windows, first-hour VWAP, same-clock relative notional, whether price holds Nov2 RTH lows, whether it rejects prior-day closing zone, whether micro uptrend becomes session higher-low; store state transition and failure timing without hindsight.
- **caveat**: Nov 2 was reviewed before thresholds were frozen, so this is retrospective descriptive demonstration, *not* an independent predictive backtest.
