# STX margin and EPS review — 2026-11-20 America/Phoenix

This review qualifies the earlier REPORT.md table. Earnings growth is evidenced; long-horizon vendor EPS is not yet a reconciled forecast.

## Material finding

ChartMill public-index table shows FY2028 gross margin55.6% and operating margin63.1%; FY2029 gross margin59.1% and operating margin65.0%. Those cannot describe one conventional income statement with positive operating expenses. Differing analyst cohorts, accounting definitions or data issues may explain this; cause remains unverified. Do not use the aggregate lines together as a financial model. Source https://www.chartmill.com/stock/quote/STX/estimates retrieved Nov20; direct long-horizon cells previously locked. Snapshot date for FY2027 history is Nov14; dates of individual long-horizon rows are unknown.

## Reverse EPS sensitivity, not guidance or an earnings forecast

| Fiscal year | Vendor revenue USD B | Vendor EPS USD | Required gross margin | EPS at57.8% gross margin |
|---|---:|---:|---:|---:|
| 2027 | 20.447 | 40.60 | 61.4% | 37.92 |
| 2028 | 28.888 | 66.50 | 68.4% | 55.51 |
| 2029 | 35.169 | 90.37 | 75.0% | 68.60 |

Assumptions, held constant across years: adjusted operating expense1.2B/year, net other expense0.1B/year, tax16%, diluted shares233M. These annualize management's December-quarter parameters, not forecasts for future years. No assumed buybacks, GAAP reconciliation or forecast of structural margin normalization. Even flat OpEx is favorable over a multiyear horizon.

Formula using USD billions: EPS=((revenue*gross_margin-1.2-0.1)*(1-.16))/.233. Required margin=(target_EPS*.233/.84+1.3)/revenue. At65% gross margin, modeled EPS is43.23/63.01/77.73. A five-percentage-point margin change moves EPS by3.69/5.21/6.34 respectively. Lower shares or taxes could reduce required margin; higher operating costs increase it.

Thus66.50 and90.37 are not established as impossible. They require stronger margins, lower share count, higher revenue or another favorable change than this fixed-input sensitivity. Confidence in volume demand must be separated from confidence in earnings per share.

## What management evidence supports

Issuer-hosted Oct27 Q1FY2027 transcript: https://s24.q4cdn.com/101481333/files/content_files/STX-US-CORRECTED-TRANSCRIPT-Seagate-Technology-Holdings-PlcSTXUS-Q1-2027-Earnings-Call-27-ET-PM-26-10-2026-2026-10-26-0.pdf
- Latest adjusted gross margin57.8%; next-quarter non-GAAP operating expense about300M, tax16%, diluted shares233M, other expense25M.
- Supply roadmap targets nearline exabyte growth around25% compounded, driven by areal density rather than increasing unit production.
- Most nearline supply allocated through calendar2028; specific pricing/configuration through calendar2027, with calendar2028 pricing still to finalize.
- Near-term gross-margin step-up is mainly pricing, while external component costs offset some manufacturing cost gains.
- Mozaic4 qualification and ramp plus Mozaic5 qualification shipments toward end-calendar2027 are execution checkpoints, not guaranteed recognized revenue.

These support growth but do not establish75% gross margin. Allocation is not fixed-price revenue. Latest-quarter profitability is not a normalized-cycle floor.

## Review and next action

Original estimates retained for provenance; this review supersedes any interpretation of them as internally reconciled forecasts. No new current quote, price input or ingestion. Existing #295 / draftPR296 scope remains unchanged.

Arithmetic: three required-margin/EPS round-trip cases independently replayed in Python after JavaScript calculation, all within1e-10. JSON parsed before publication. No calibrated probability, GAAP model, fair value or integration claimed.

Next: obtain same-cohort adjusted consensus inputs and long-horizon diluted-share assumptions; independently verify whether pricing/capacity contracts support required margins.
