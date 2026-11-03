# October 2026 compression and failed-stabilization study (research only)

Spark B06 · issue #144 · November 3, 2026 · provider: Massive Stocks completed historical daily and 1-minute OHLCV · **not a deployed strategy or calibrated predictor**.

## Hypothesis
Price traverses nested liquidity ranges. A slowdown in net downward basis points per USD billion traded is an *absorption candidate*, not an automatic floor. A candidate becomes a failed-stabilization event if a subsequent completed bar violates the provisional defended low before a defined higher-low confirmation. Its failure is known only at breach time; all prior snapshots remain candidates.

## Verified October daily cross-section (Oct 1 closing price -> Oct 30 closing price)
| Ticker | Endpoint change | Largest selected down days |
| --- | ---: | --- |
| SPY | -1.08% | Oct 14 -1.08%; Oct 16 -1.11%; Oct 22 -1.18%; Oct 30 -1.77% |
| SMH | -15.43% | Oct 14 -3.98%; Oct 16 -3.41%; Oct 22 -5.99%; Oct 30 -6.98% |
| ORCL | -5.36% | Oct 14 -8.83%; Oct 16 -4.64%; Oct 30 -6.37% |
| AAOI | -35.66% | Oct 14 -11.82%; Oct 22 -11.96%; Oct 30 -12.80% |
| AMD | -18.02% | Oct 14 -5.73%; Oct 16 -5.95%; Oct 22 -8.10%; Oct 30 -10.88% |
| MU | -19.38% | Oct 16 -5.63%; Oct 22 -6.26%; Oct 30 -5.30% |
| MSFT | +1.78% | Oct 16 -1.93%; Oct 22 -2.23%; Oct 30 -1.55% |
| HYG | +0.69% | Oct 14 -0.36%; Oct 16 -0.35%; Oct 30 -0.19% |

These endpoints are not conventional October monthly returns: they omit Sept 30 to Oct 1. Some daily instruments requested (NVDA, CRWV, AVGO) were not available in this specific batch; do not silently fill gaps.

## Verified 1-minute regular-session cases (9:30–16:00 ET only)
Massive one-minute historical bars; notionals sum minute VWAP × shares, **all two-sided traded value**, not net buyer/seller flow. Closing values are last minute-bar closes (may differ from official auction).
| Date | Ticker | Low | Low time ET | Last minute close | Close location in full-day range | RTH notional |
| --- | --- | ---: | --- | ---: | ---: | ---: |
| Oct 16 | QQQ | 707.23 | 15:08 | 709.86 | 14.0% | $42.53B |
| Oct 16 | SMH | 539.07 | 15:08 | 539.62 | 3.5% | $9.19B |
| Oct 30 | QQQ | 683.45 | 14:52 | 690.53 | 46.6% | $47.37B |
| Oct 30 | SMH | 511.63 | 14:35 | 522.83 | 47.3% | $8.06B |

**Distinct morphology:** Oct 16 ended close to lows; Oct 30 recovered much further from lows, despite severe losses. A day-level down return, net impact, or close location alone cannot certify failed or sustained intraday stabilization. At least one preliminary 15-minute bounce on Oct 30 was followed by a lower low before recovery; the full sequence must be preserved rather than replacing it with the terminal-day label. Oct 16 SMH had two simple 15-minute rebound candidates followed by breach of the prior running low; these were exploratory candidates, not validated signals.

November 2 (reserved as illustrative future holdout after October rule freeze): official daily lows QQQ 680.33, ORCL 118.43, NVDA 201.66; final 30-minute RTH notch QQQ ~$4.84B, ORCL ~$1.10B, NVDA ~$3.12B traded notional; new lows continued late. Do not use Nov 2 to tune Oct thresholds and then call it out-of-sample.

## Event ontology (candidate v0, not approved shared schema)
- `downward_expansion`: negative rolling return, increasing negative signed price impact magnitude, and time-of-day-normalized turnover elevated; distinguish realized path from close-to-close movement.
- `absorption_candidate`: new/equal low or test of pre-declared zone, elevated notional, falling net downward displacement per notional; cannot assert signed institutional buying from OHLCV.
- `stabilization_attempt`: completed bounded interval holds defended low and reclaims a predeclared fraction of the decline; timestamp event available when interval completes.
- `failed_stabilization`: later **first completed breach** of the defended low, within frozen evaluation horizon, before sustained higher-low/higher-high confirmation; record breach and subsequent impact separately.
- `successful_defense`: no breach over frozen horizon *and* positive trend confirmation; otherwise `unresolved` rather than success.
- `downward_continuation`: next lower low following failed stabilization; continuation speed may be measured but is not presumed.
- `reversal_confirmed`: predeclared higher-low/higher-high structural change plus measured directional buying and volume validation if entitled tick flow is available; without signed flow mark confirmation limited.

## Four non-substitutable measurements
1. `r_bp = 10000 * ln(P_end / P_start)`: signed net displacement, price scale-independent.
2. `turnover_usd = Σ minute_v × minute_vwap`; `impact = r_bp / (turnover_usd / 1e9)`; never interpret as dollar net flow or Kyle's lambda estimate without appropriate assumptions.
3. `path_efficiency = abs(log(P_end/P_start)) / Σ abs(log(P_i/P_{i-1}))`: cancellation/oscillation sensitivity; 0–1 when path nonzero. Pair with realized volatility/range.
4. `activity_ratio = turnover_window / median(turnover_same_clock_windows_previous_20_sessions)`: time-of-day adjustment; fail closed when history insufficient. Also measure directional change of impact, normalized price velocity, zone touch count and low breach.

## Deterministic detection protocol and falsification
- Entire universe fixed before evaluation (QQQ, SPY, SMH, NVDA, AMD, AVGO, ORCL, CRWV, AAOI, MU, MSFT, HYG plus eligible controls). Validate exact prices, splits, bar omissions; no winner-only selection.
- Partition chronology: formation Oct 1–15, stress tests Oct 16–29; independent later holdouts Oct 30 and Nov 2 **only if thresholds were actually frozen before scoring**, otherwise mark retrospective demonstration. Better: multi-month walk-forward with purged/embargoed event labels to avoid lookahead.
- Pre-register common clock-aligned 5/15/30-minute windows and defend-zone boundaries. Sweep 0.25/0.5/1.0 × preceding intraday realized range; horizons 15/30/60/120 minutes. Show sensitivity rather than pick the favorable threshold.
- Evaluate precision/false-positive rate, detection lead time, missed recoveries, event clustering, per-symbol baseline, sector residuals versus QQQ/SMH, high/low sequence and relative notional.
- Compare baseline: price-only lower low, drawdown/ATR, volume spike, VWAP rejection, Hurst/change-point alternatives, and holdout bounce/rebound costs. A close below prior low alone is not a detector of *absorption*.
- Stress high-volume close auctions, opening gap, stale/delayed data, missing minute bars, thin liquidity, splits, price-limit jumps, duplicate bars, volume adjusted vs price adjusted, large spreads and unknown trade aggressor.
- Equity trading notional does not equal capital inflow/outflow; trade signs and order-book resistance require entitled trade-and-quote / NBBO data.
- Event snapshots must carry `observed_at`, `available_at`, `ingested_at`, `as_of`, `model_version`, `source`, `source_class`, `input_manifest_hash`, quality status, ticker, session and expiration/TTD.

## Integration
Read-only evidence handoff to B06 #108/PR109 and B10 #95/PR99. Shared event schema requires B00; cross-domain integration tests B01; parameter calibration B07 #93; market-data observations B02. Do not modify others' files or claim live detection. Next task: deterministic replay on full October RTH minute bars for entire fixed universe, then point-in-time walk-forward scoring and independent test execution.
