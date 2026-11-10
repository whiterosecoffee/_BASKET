# NVDA, CRWV, SMH and QQQ: actual performance and relationships

**Price cutoff: November 9, 2026 close.** Research captured November 10. USD; split-adjusted price returns, **not** dividend-reinvested total returns. No current-day partial prices or pre/after-hours prices mixed into this comparison.

## What the comparison says

CRWV had the largest decline over the last 20 and 60 matched sessions. NVDA also underperformed both ETFs. Yet on November 9, NVDA fell while the other three rose. A shared AI theme and real corporate links do not make these securities interchangeable.

| Matched close-to-close window | NVDA | CRWV | SMH | QQQ |
|---|---:|---:|---:|---:|
| 1 session, Nov 6–Nov 9 | -4.27% | +5.56% | +5.05% | +3.54% |
| 5 sessions, Nov 2–Nov 9 | -11.58% | -2.33% | -4.11% | -0.26% |
| 20 sessions, Oct 12–Nov 9 | -21.05% | -38.97% | -17.53% | -8.94% |
| 60 sessions, Aug 14–Nov 9 | -20.65% | -53.47% | -17.08% | -7.07% |

Over the 20-session window, NVDA lagged QQQ by **12.12 percentage points**, CRWV by **30.03 points**, and SMH by **8.59 points**. These are differences of cumulative price returns, not risk-adjusted alpha or causal attribution.

## How closely their daily movements matched

Pearson correlation of **60 paired arithmetic daily returns**, using 61 closes from August 14 through November 9. This measures co-movement, not similarity of price levels or proof of an economic mechanism.

| Pair | Correlation |
|---|---:|
| NVDA / CRWV | 0.44 |
| NVDA / SMH | 0.75 |
| NVDA / QQQ | 0.65 |
| CRWV / SMH | 0.74 |
| CRWV / QQQ | 0.65 |
| SMH / QQQ | 0.91 |

The ETFs moved most closely together in this sample. NVDA/CRWV had the weakest correlation of these six pairs despite their documented business and investment relationship. Correlations can change with the chosen window and are not forecasts.

## Verified relationships, separately from correlations

- **SMH → NVDA:** [VanEck's issuer holdings file](https://www.vaneck.com/us/en/investments/semiconductor-etf-smh/downloads/holdings/) reports NVDA at **18.91% of SMH net assets on November 9, 2026**. That is a fund allocation, not SMH owning 18.91% of NVIDIA. The complete supplied list contains 25 stock rows and two cash/other rows; CRWV is not listed.
- **QQQ → NVDA:** [Invesco's holdings page](https://www.invesco.com/qqq-etf/en/about.html) reports NVDA at **7.11% on November 8, 2026**. Only its top ten holdings were retrieved. NVDA, AMD and Micron appear in both inspected ETF lists. Full QQQ overlap and CRWV membership remain unresolved. The different snapshot dates are not silently treated as identical.
- **NVDA → CRWV:** [NVIDIA's January 26, 2026 announcement](https://nvidianews.nvidia.com/news/nvidia-and-coreweave-strengthen-collaboration-to-accelerate-buildout-of-ai-factories) states a **$2 billion investment in CoreWeave Class A stock at $87.20 per share**, alongside expanded collaboration using NVIDIA infrastructure. It does not establish NVIDIA's current ownership percentage. The stated ambition for more than 5 GW by 2030 is forward-looking, not completed capacity.

These holdings snapshots are context at their stated dates, not beginning-of-period weights. They are **not used to explain or attribute** the historical ETF returns. No investment recommendation is made.

## Small, reusable increment

This is a research consumer of the existing [B17 market-context component, PR101](https://github.com/whiterosecoffee/_BASKET/pull/101), not another engine or market-data store. It loads the existing `change(price, baseline)` helper from its pinned Git blob and uses Python's standard-library correlation. Original owner files and shared contracts remain unchanged. Scope handoff: [issue 217](https://github.com/whiterosecoffee/_BASKET/issues/217), linked to [issue 100](https://github.com/whiterosecoffee/_BASKET/issues/100).

Files:
- `result-2026-11-09.json`: machine-readable returns, relative performance, correlations and missing-data flags.
- `sources-2026-11-10.json`: requests, input hash, pinned dependency, dated relationships and limitations.
- `compare.py`: small reproducible consumer; no network fetch, polling, persistence or order execution.
- `test_compare.py`: five focused checks, not 94 valuation tests.

Those five tests guard exact windows/arithmetic, missing data without forward-fill, future/duplicate dates and absent cutoff, invalid/intraday input, and constant/short series. All five passed locally. Real input replay additionally matched 16 returns against Decimal arithmetic and six correlations against pandas and a separate JavaScript calculation. This checks the calculation, **not** investment merit, forecast accuracy or provider correctness. No independent CI or integrated-main claim is made.

## Reproduce without committing licensed raw prices

Fetch each symbol through the entitled Massive connector:

`/v2/aggs/ticker/{NVDA|CRWV|SMH|QQQ}/range/1/day/2026-07-01/2026-11-09`

Use `adjusted=true`, `sort=asc`, `limit=50000`. Each returned 92 daily rows. Join on the source timestamp, retaining and reporting missing observations; verify the intersection is all 92 dates before reproducing this particular result. Save private CSV columns `t,NVDA,CRWV,SMH,QQQ`. Four final daily closes were cross-checked against `/v1/open-close/{ticker}/2026-11-09`, excluding `afterHours` and `preMarket`. Do not publish the raw CSV or bars.

From a checkout with the pinned dependency commit available:

```sh
git show 565e582720a32d8d73c5421d6d99d503c4bbde03:engines/composites/market_context/context.py > /tmp/basket-context.py
python research/composites/market_context/ticker_comparison/compare.py \
  --csv /private/path/comparison-input.csv \
  --context-module /tmp/basket-context.py \
  --cutoff 2026-11-09 --evaluated-at 2026-11-10T20:31:02.679Z
python -m unittest discover -s research/composites/market_context/ticker_comparison -v
```

The module's Git blob is verified before import. The commit is on PR101, not necessarily in a default main-only checkout. Missing dependencies fail explicitly. A later provider correction can legitimately change the input hash and result; retain it as a new dated research revision rather than overwrite this snapshot.

## Limits that remain visible

- All four source series align on 92 dates with zero ticker-specific gaps. An independent exchange-calendar completeness check was not performed; shared omissions across all four series cannot be disproved by alignment alone. Window labels count supplied aligned trading dates.
- Price cutoff and research time are distinct. Data were retrieved on November 10 using then-current historical revisions. Original publication/ingestion vintages are unknown: **this is not a point-in-time backtest**. Later information was not used to manufacture a historical forecast.
- Split adjustment does not reinvest dividends. Observed ETF prices already embed ongoing expenses and tracking effects; the comparison subtracts no second fee drag. Execution costs and taxes are excluded.
- First publication times for the issuer holdings snapshots are unknown. Their dated values are research context, never earlier backtest inputs.
- No full same-date ETF overlap, historical constituent attribution, current NVDA ownership percentage in CRWV, or continuous live service is established. B02 remains responsible for canonical source adoption; B04 valuation work is unchanged.
