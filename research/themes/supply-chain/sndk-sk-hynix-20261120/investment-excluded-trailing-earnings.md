# Investment-excluded trailing earnings comparison
Research model v3, as-of November 20, 2026 America/Phoenix; retrieved November 21 UTC. B19 #309, branch work/309-sndk-sk-hynix-comparison, draft PR #310. This supersedes the provisional SKHY USD18.07/5.73x vendor baseline in us-footprint-trailing-pe.md for this explicit FX convention.

## Result
At previously sourced Nov 20 regular closes SNDK USD79.24 and SKHY USD103.57:
| Basis | SNDK | SKHY ADS |
|---|---:|---:|
| Reported diluted trailing EPS, reconstructed USD | 15.59375 | 19.59700 |
| Reported trailing P/E | 5.0815x | 5.28499x |
| Investment-excluded EPS, estimated tax effects | 14.66605 | 14.99258 |
| Investment-excluded trailing P/E | 5.40295x | 6.90808x |
| Also remove SK financing derivative gains/losses | unchanged | EPS15.96839; PE6.48594x |

SNDK has approximately 17–22% lower P/E under these modeled adjustments. This ranks quoted US securities, not Korean ordinary-share entry economics. It does not establish future return superiority, fair value, or through-cycle margins. SK gains are real assets/returns, excluded only from recurring semiconductor earnings; not erased from net asset value.

## Convention and limitations
Use latest completed four-quarter windows: SNDK through Oct 2, 2026; SK through Sept 30, 2026. Retain stock compensation, R&D, depreciation, operating costs and ordinary interest. No automatic adoption of issuer non-GAAP EPS. SK K-IFRS versus SNDK US GAAP remains an accounting difference; capitalized development policy is not harmonized.
SK ADS = 0.1 ordinary share. Convert ALL trailing KRW EPS at Nov 20 USD/KRW1346.16 (Investing.com daily closing observation). This is a valuation retranslation using one explicit date-matched spot rate, not historical average-rate USD EPS. Supersedes unverified vendor USD18.07; do not imply vendor mistake without knowing its methodology. Spot FX and equity closes are date matched but not tick synchronized.
No new quotes/JSONL or ingestion adapters created. FETCH runtime unavailable in this session; prices remain identified third-party web observations, not validated canonical feed outputs. SNDK close conflicts with historical chat USD78.65; analysis uses explicitly sourced USD79.24.
Quarter EPS summation and inferred Q4 weighted shares are approximate due to rounding and changes in dilution. Q4 SK shares inferred using equal-quarter time weights, not issuer reported exact Q4 daily weights. This does not materially explain the observed gap, but limits precision.
Tax on each removed item is NOT separately disclosed in reviewed tables. Base case applies reported effective tax rates to adjustments for the matching periods. This is an estimate, not an audited recurring EPS reconciliation. NCI/investment attribution is assumed parent-level for screening; minor exact attribution not separately reconciled.

## SNDK bridge (USD millions before split)
Four-quarter GAAP EPS (5.15 + 23.03 + 43.97 + 52.60)/8 = 15.59375.
TTM GAAP net income = FY26 11433 - FY26Q1 112 + FY27Q1 8101 = 19422.
TTM equity securities gains = FY26 808 - FY26Q1 0 + FY27Q1 513 = 1321.
FY26Q3 equity gains zero, FY26Q4 804, so residual FY26Q2 = 4.
Period tax assumptions:
- FY26Q2 134/937 = 14.301%;
- FY26Q4 946/7849 = 12.052%;
- FY27Q1 1218/9319 = 13.070%.
After-tax investment gain per post-split share =
[4*(1-134/937)/156 + 804*(1-946/7849)/157 + 513*(1-1218/9319)/154]/8 = 0.92769569.
Gain-excluded EPS = 15.59375 - 0.92769569 = 14.66605431; P/E = 79.24/EPS = 5.40295.
This retains SBC and other costs excluded from company adjusted EPS. A broader financing normalization could also add back FY26Q3 debt-extinguishment expense USD46m after tax; this changes rounded P/E only modestly and is not needed to establish rank.

## SK bridge (KRW millions unless shares)
TTM construction = FY2025 - 9M2025 + 9M2026.
From finance notes:
| Item | FY2025 | 9M2025 | 9M2026 | TTM |
|---|---:|---:|---:|---:|
| Valuation gains | 12012137 | 5384696 | 40261061 | 46888502 |
| Dividend income | 940739 | 12033 | 13985795 | 14914501 |
| Disposal gains | 187868 | 138580 | 472483 | 521771 |
| Valuation losses | 27913 | 310 | 4908 | 32511 |
| Investment-specific FX losses | 247087 | 39924 | 5669112 | 5876275 |
Net pretax investment contribution = gains + dividends + disposals - valuation losses - investment FX losses = 56415988 (KRW56.416T). Equal USD41.91B at chosen spot, NOT period-average translated accounting income.
Q4 contribution = 7370669; 9M26 contribution = 49045319.
Ordinary operating FX is retained; ONLY identified investment-asset FX is removed. Valuation/disposal categories may contain small nonstrategic financial assets, so this is broad financial-investment screening rather than exact Kioxia-only attribution.
Q4 tax rate = (7517650-5110291)/(50465552-32812240) = 13.6369%.
9M26 tax rate = 50989618/225033713 = 22.6587%.
Q4 inferred diluted ordinary shares = 4*711266733 - 3*711232778 = 711368598.
9M26 diluted ordinary shares = 715236972.
Reported reconstructed TTM EPS KRW = 60378 - 38850 + 242279 = 263807.
USD/ADS EPS = 263807/1346.16/10 = 19.59700.
Investment EPS removed KRW/ordinary =
7370669*(1-Q4tax)*1e6/711368598 + 49045319*(1-9M26tax)*1e6/715236972.
USD/ADS recurring proxy = (263807 - removed)/1346.16/10 = 14.99258.
SKHY investment-excluded P/E = 103.57/14.99258 = 6.90808.

## Symmetric financing-loss normalization
SK annual prospectus says derivative losses relate primarily to exchangeable bonds and were noncash; a broader recurring-earnings screen should not retain these financing marks while removing investment marks.
Q4 net derivative loss = (8365976-397) - (390-34) = 8365223.
9M26 net derivative loss = 3979490 - 1223438 = 2756052.
Add back both net losses using same period tax rates and diluted shares.
EPS becomes USD15.96839/ADS; P/E6.48594.
This is an explicitly broader variant. Do not call financing derivative losses an offset to Kioxia investment gains; the mechanisms differ. Do not add back contractual interest or dilution costs twice.

## Tax sensitivity, not confidence intervals
If removed items have 0–30% tax effects rather than the base effective-rate allocation:
- SNDK investment-excluded P/E 5.3353–5.4520x.
- SK investment-excluded P/E 6.6852–7.5415x.
- SK with financing derivative normalization 6.3523–6.9542x.
Rank remains SNDK cheaper within tested tax scenarios and selected FX convention. These are assumption ranges, not audited tax bounds. Future NAND/HBM margin declines can raise multiples further; investment adjustment is not cycle normalization.

## Evidence
Primary:
1. Sandisk Jan 29 FY26Q2 results: https://www.sandisk.com/company/newsroom/press-releases/2026/2026-01-29-sandisk-reports-fiscal-second-quarter-2026-financial-results
2. Sandisk Aug 5 FY26Q4 results and full-year bridge: https://www.sandisk.com/company/newsroom/press-releases/2026/2026-08-05-sandisk-reports-fiscal-fourth-quarter-2026-financial-results
3. Sandisk Oct 29 FY27Q1 results and split: https://www.sandisk.com/company/newsroom/press-releases/2026/2026-10-29-sandisk-reports-fiscal-first-quarter-2027-financial-results
4. SK SEC prospectus July 2026, consolidated FY25 notes27,29,30: https://www.sec.gov/Archives/edgar/data/2120882/000119312526299963/d32785d424b4.htm
5. SK Nov 2026 6-K, consolidated interim finance note24 and EPS note27: https://www.sec.gov/Archives/edgar/data/2120882/000119312526461909/d166755d6k.htm
Third-party dated observations:
6. SNDK Nov20 regular close: https://stockanalysis.com/stocks/sndk/
7. SKHY Nov20 close: https://ph.investing.com/equities/sk-hynix-adr-historical-data
8. Nov20 FX1346.16: https://www.investing.com/currencies/usd-krw-historical-data

## Review and next action
Arithmetic recomputed with Python and independent JS sensitivity calculations. No executable production changes, no tests added. Exact investment-specific tax effects, fully synchronized canonical quotes, exact Q4 dilution, independent CI and IFRS/GAAP accounting normalization remain unverified.
Next: compare 2027/2028 recurring EPS under common NAND/HBM pricing and margin stress rather than extrapolate peak trailing profits.
