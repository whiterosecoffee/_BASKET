# CRWV — conditional time to 2×/3×/4×/5×
As-of 2026-11-20, 16:00 ET close. Research-only scenario, not trading advice, automated forecast, or confirmed result.
Spark B10 / issue #113 / draft PR #114. Reuses #86/PR87 economics engine (not edited), #68/PR69 funding work, and #115 peer adapter handoff.

## Price reference and milestones
CRWV close $39.51 on Nov 20, 2026 (StockAnalysis and Yahoo Finance). Source https://stockanalysis.com/stocks/crwv/ and https://finance.yahoo.com/quote/CRWV/. Intraday low $39.28; aftermarket prices may change and are excluded from the close-basis scenario.
2x $79.02; 3x $118.53; 4x $158.04; 5x $197.55. Arithmetic is exact off $39.51, no forward forecasts implied.

## Primary operating baseline (Q3, published Nov 10 2026)
CoreWeave release https://www.sec.gov/Archives/edgar/data/1769628/000176962826000461/coreweave3q26earningspress.htm
Revenue $3.661B; adjusted EBITDA $2.256B; GAAP operating income $207M; net interest expense $846M; net loss $709M; backlog $132.5B, subject to service delivery/availability; contracted power >4.6GW including operational capacity; active power >1.7GW. Approximately >2.9GW contracted less active is a *not-yet-active* gap, not billable inventory. FY26 revenue guidance $13.0–13.3B; exit annualized run-rate revenue $20–21B, not identical to full-year recognized revenue. FY26 capex guidance $37–39B; Q4 net interest guidance $1.05–1.15B. ATM program up to 35M Class A shares; potential additional convertible dilution; no automatic assumption of all shares issued.
Q3 SEC 10-Q https://www.sec.gov/Archives/edgar/data/1769628/000176962826000465/crwv-20260930.htm: scheduled total debt principal $47.505B, of which remainder 2026 $2.433B, 2027 $10.974B, 2028 $5.479B (gross debt payment schedule, not necessarily net debt). Cash and equivalents Sep 30 $4.122B; facility available capacity $5.653B, neither unrestricted cash flow nor assured future financing. Cash generated from operations nine months $5.6B reflects customer cash timing; investment outflows $24.7B; financing inflows $21.3B.

Analyst baseline: Nov 20 S&P Global Market Intelligence consensus at https://stockanalysis.com/stocks/crwv/forecast/: FY26 revenue $13.11B, FY27 revenue $27.10B and adjusted EPS FY27 -$1.77. The 2028 $43.5B revenue used below is a *scenario modeling input based on earlier pre-Q3 forecasts*, not a verified current FY28 consensus.

## Timing bands: conditional milestones, never empirical probabilities
- 2x ($79): possible in 2027–2028 if bookings become billable, funding is reliable and valuation normalizes; a speculative price reaction can occur sooner, but fundamentals do not justify a forecast date.
- 3x ($119): conceivable 2028–2029 if FY27 >$27B is approached and FY28 approaches $40–45B while debt and dilution stabilize.
- 4x ($158): 2029–2031 growth scenario requiring material equity cash-flow conversion and competitive economics across GPU fleet renewal.
- 5x ($198): 2030–2032+ high-execution scenario requiring sustaining large revenue, reduced funding costs, share count discipline and credible replacement economics.
- Bear/negative branch: none of these targets reached; financing/refinancing/dilution and hardware obsolescence can permanently impair current equity.

## Reverse enterprise-value requirements (illustrative, NOT forecast)
Assume fully diluted shares S=0.650B and net senior claims N=$55B at *valuation date*, where net claims include debt less unrestricted cash and any other senior interests; neither is an observed 2028 fact. Hypothetical FY28 revenue R=$43.5B; implied equity P×S, enterprise value EV=P×S+N.

Target | Equity ($B) | Required EV ($B) | EV/FY28 R
2x $79.02 | 51.36 | 106.36 | 2.45x
3x $118.53 | 77.04 | 132.04 | 3.04x
4x $158.04 | 102.73 | 157.73 | 3.63x
5x $197.55 | 128.41 | 183.41 | 4.22x

Not a DCF or fair value. A larger FY28 share count increases the required EV; an additional $10B of senior net claims increases the required EV by $10B; a lower achieved revenue/multiple delays or invalidates milestones. Gross debt, equipment leases, lender collateral, convertible obligations, new equity and unfunded capex need an explicit reconciled waterfall, not a simplistic 2028 net claim.

## Gates to higher confidence
1. Q4 FY26 actuals confirm exit run rate/2027 guidance and billable, not just contracted, growth.
2. Track month-by-month MW power rights→energized→cluster accepted→billable, with tariff cohorts.
3. Reconcile 2027 $10.974B scheduled principal, interest, available vs drawn project financing, customer deposits, and capex (do not treat prepayments as profits).
4. Estimate GPU residual and renewal/maintenance capex, normalized post-depreciation operating profits and economic ROIC.
5. Fully diluted equity bridge: Class A/B shares, issued ATM shares, convertibles, SBC, and possible future capital raises.
6. Compare NBIS and IREN using consistent per-billable-MW equity return and project funding metrics before calling CRWV best-in-class.
7. Timestamp sources, use TTD, distinguish current close from afterhours and no percentile/probability claims without walk-forward evidence.

## Interpretation
Revenue scale alone makes a 2x or even 5x *arithmetically possible*, not probable: shareholder outcomes are levered to future net financial claims and diluted shares. Cannot establish calibrated milestone arrival probabilities or exact dates from current filings. Prior analysis based on Q2 values superseded here by Q3 actuals, not deleted.
