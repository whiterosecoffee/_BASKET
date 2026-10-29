# GDYN versus CRWV: dated growth and price comparison

As of 2026-10-29 regular-session close, USD. Research observation, not a live feed. Issue #116. Provisional GDYN company research scope; formal spark/catalog registration pending B00.

## Price evidence
| Metric | GDYN | CRWV |
|---|---:|---:|
| 2026-10-29 close | 9.49 | 60.74 |
| 2026-10-28 close | 8.75 | 63.93 |
| 2026-10-29 close-to-close | +8.46% | -4.99% |
| Reported one-year return (third party, approximate) | +17.2% | -54.8% |
| 52-week low | 5.11 | 51.24 |
| 52-week high | 10.21 | 138.36 (provider-dependent) |
| Drawdown versus cited high at close | -7.1% | -56.1% |

Sources: https://stockanalysis.com/stocks/gdyn/ ; https://stockanalysis.com/stocks/crwv/history/ ; https://www.stocktitan.net/overview/GDYN/ ; https://markets.financialcontent.com/wss/quote/nq%3Acrwv . One-year performance figures are indicative, not jointly recomputed from matched adjusted prices; a strict cross-ticker return series requires B02 date-aligned bars and corporate-action checks. All dates above are market effective dates; retrieval date 2026-10-29; first-available/ingested provider timestamps unknown (null). No claim of live TTD validity.

## GDYN earnings and growth
Company Q3 2026 press release filed in 8-K on 2026-10-29, period end 2026-09-30: revenue $114.3m (+9.7% YoY; +5.7% QoQ); AI revenue share 31%, implies ~$35.43m AI revenue (derived); issuer states AI revenue has grown >45% YoY for three quarters. GAAP gross margin 40.3% vs 33.3% a year ago; non-GAAP EBITDA $22.9m / 20.0% revenue vs $12.7m / 12.2%; adjusted EPS $0.18 vs $0.09; GAAP income $6.2m vs $1.2m. Nine-month operating cash flow $30.5m versus $30.7m. Cash $304.3m. Repurchases $35.5m for 5.3m shares in nine months. Q4 revenue outlook $113.5m–$115.5m (flat sequential at midpoint) and EBITDA outlook $20m–$22m (below Q3): do not extrapolate one quarter EPS annualization into guidance.

Source (SEC 8-K with furnished exhibit): https://www.stocktitan.net/sec-filings/GDYN/8-k-grid-dynamics-holdings-inc-reports-material-event-9b7f7ec68175.html ; mirrored press release https://www.marketscreener.com/news/grid-dynamics-reports-record-third-quarter-2026-financial-results-ce785fdadd81fe2c . Class: company statements and company-reported GAAP/non-GAAP measurements. EPS adjustments, especially share compensation, prevent treating adjusted EPS as cash earnings.

## CRWV fundamental comparison and valuation caveats
CRWV is GPU infrastructure / cloud capacity provider, with contracted capacity needing financing, energization, commission and billability. GDYN is enterprise delivery/consulting; less direct GPU capex/debt burden. They are **not** same-sector earnings-multiple comps. GDYN currently exhibits favorable share-price momentum while CRWV exhibits much larger 12-month drawdown; this does not establish GDYN's superior future return. CRWV latest matched quarterly revenue, adjusted EPS, net debt, issued share count, contracted/active/billable MW and liquidity runway are not independently verified in this research snapshot; do not invent values. Read existing B10 dated CRWV research before subsequent extension.

## Valuation and falsifiers
GDYN $9.49 / ($0.18 * 4) = 13.18x Q3 *annualized* non-GAAP EPS run-rate; **not** a trailing or consensus forward P/E. The numerator is a dated close; the denominator is a one-quarter extrapolation and potentially optimistic given Q4 outlook. Companywide growth 9.7% versus issuer AI growth >45% implies a possible legacy-business drag; requires AI segment consistency and customer mix. GDYN bull falsifiers: AI revenue share stalls, GAAP and cash EPS fail to track adjusted margin, Q4 EBITDA contraction persists, consulting work commoditizes. CRWV bull falsifiers: financed/billable capacity does not convert, debt/refinancing costs exceed cohort unit economics, dilution erases enterprise value gains. Compare return on invested equity and *cash* earnings after financing rather than relying on revenue growth alone.

## Reproduce / remaining tests
1. GDYN 2026-10-29 return = 9.49/8.75 - 1 = 8.4571%; CRWV = 60.74/63.93 - 1 = -4.9898%.
2. GDYN high drawdown = 9.49/10.21 - 1 = -7.052%; CRWV = 60.74/138.36 - 1 = -56.10%.
3. Strict 1M, 3M, 6M, YTD, 1Y comparative prices need date-matched adjusted close inputs from B02, unavailable here; no fabricated tape.
4. CI/exact-head runner not yet verified. No runtime connector, market database modification, event/edge registration, or canonical ticker entity created.

## Hand-offs
B00: register a GDYN company spark and assign isolated paths, decide entity contract/catalog indexing. B02: initialize GDYN price history from entitled source with 200+ sessions if available and compare with CRWV adjusted series. B04: own comparable forward earnings/FCFE scoring rather than reusing this research note as a valuation engine.
