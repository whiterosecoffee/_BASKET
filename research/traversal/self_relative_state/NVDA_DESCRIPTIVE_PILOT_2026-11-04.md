# NVDA historical-state descriptive pilot — 2026-11-04

**Scope:** B06 #154 experimental self-relative research, no production implementation or validated trading signal. Source: Massive Stocks Custom Bars `GET /v2/aggs/ticker/NVDA/range/1/day/2024-10-01/2026-11-04?adjusted=true&sort=asc&limit=50000` and identical QQQ query. Returned **526** completed-dated records for each instrument, first date 2024-10-01, last date 2026-11-04. Calculations were run in Massive temporary SQL workspace in the conversation on 2026-11-04, not a committed market-data dataset. The historical `available_at`, corrections, session qualification and full as-of replay contract were **not** supplied; this is a retrospective/provisional description only, **not** the strict #154 PIT backtest. Daily-bar UTC timestamps represent session dates, not observed/available capture times. Provider response data and SQL outputs were reviewed, but raw bars are not duplicated here.

## 2026-11-04 close and cross-horizon state
| Field | NVDA |
|---|---:|
| Adjusted closing price (USD) | 200.13 |
| SMA10 | 209.9670 |
| SMA30 | 221.2327 |
| SMA200 | 204.6722 |
| Distance to SMA10 | -4.685% |
| Distance to SMA30 | -9.539% |
| Distance to SMA200 | -2.219% |
| SMA30 change over last 5 completed sessions | -1.429% |
| SMA200 change over last 5 completed sessions | +0.262% |
| 200D displacement past-only midrank percentile (252 previous eligible computed distances) | 1.98th |
| 5/10/30-session total price changes | -7.081% / -9.839% / -11.254% |
| Current session volume / 20-session average volume including current session | 1.434x |
| Simple 14-session mean of true ranges (NOT Wilder ATR14) | $6.511 |
| Price-SMA200 / above simple true-range proxy | -0.698 |

**Important:** The simple true-range mean is a proxy, *not* the exact Wilder ATR14 specified in `RESEARCH_CONTRACT.md`; do not substitute it in a contractual ATR field. Empirical midrank uses prior 252 computed SMA200 distances (252/252), with provisional retrospective adjustment history; rank is not a forward return probability.

## Aligned QQQ comparison
For the same 526-date adjusted-bar coverage, latest QQQ closing price $691.95. Synchronized simple returns:
| Horizon | NVDA | QQQ | NVDA vs QQQ ratio return |
|---|---:|---:|---:|
| 5 completed sessions | -7.08% | -4.64% | -2.56% |
| 10 completed sessions | -9.84% | -4.58% | -5.51% |
| 30 completed sessions | -11.25% | -6.65% | -4.94% |

Ratio-relative return is computed as `100*((NVDA_current/NVDA_prior)/(QQQ_current/QQQ_prior)-1)`; this is **not** beta-adjusted alpha, sector-adjusted residual or future directional inference.

## Historical configuration exploration (NOT held-out validation)
A deliberately coarse retrospective screen over this same adjusted daily sample required:
- At least 205 rows to support 200D MA plus five-session slope;
- Current completed close < SMA200 and SMA30;
- SMA200 5-session slope > 0 and SMA30 5-session slope < 0;
- SMA200 close displacement within [-5%,0%).

The screen found 13 qualifying days inclusive of Nov 2 and Nov 4, with **11** older days having completed forward windows. However, ten of those 11 historical observations were clustered around March–April 2026, with one on July 29 2026. Treat these as at most **two** historical episodes, not 11 independent analogues. Illustrative nonindependent dated outcomes: March 20 2026 → five-session price change -3.00%, ten-session +2.86%; July 29 → +15.37% and +17.94%. November events have no full forward five/ten-session resolution and remain censored. Sample too thin and selected retrospectively to support predictive probability or trading advantage.

## What was actually tested / not tested
**Computed and observed:** SMA levels/distances/slopes; 252-prior-observation percentile; synchronized QQQ-relative returns; descriptive conditions; retrospective analogues. Numerics should be reproduced under a frozen SQL/engine version before model adoption.

**Not executed:** #154's primary controlled B06 traversal-only vs traversal+SMA30-slope paired test; #145 frozen battle episode/label manifest; signed order flow, volume-at-price, trade-level activity, independently executed domain tests, point-in-time source replay and B07 calibration. Do not interpret the 1.98th percentile as proof of rebound. A single low-displacement observation may continue falling.

## Source and reproduction instructions
Massive API: `/v2/aggs/ticker/{ticker}/range/1/day/2024-10-01/2026-11-04`, parameters `adjusted=true,sort=asc,limit=50000` for both `NVDA` and `QQQ`. Confirm stock adjustment/corporate actions and session calendars with B02. Compute rolling SMAs from completed closes; use `close/SMA_N-1`, `SMA_N(t)/SMA_N(t-5)-1` and rank of last SMA200 deviation strictly against preceding 252 valid SMA200 deviations (ties midrank). Report source/revision hashes and first-available timestamps before promoting to strict PIT replay. Store any subsequent production analytic result in approved ticker-home or B06 output path only after B00/B02 contracts.

**Disposition:** descriptive NVDA pilot succeeded; predictive incremental benefit **NOT VERIFIED**, canonical PIT replay **BLOCKED**. This document records calculations without copying the provider's bar series. B00/B02 #148, B06 #144 and B07 #93 remain the receiving dependencies.
