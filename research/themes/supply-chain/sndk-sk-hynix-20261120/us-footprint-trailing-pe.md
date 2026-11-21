# Headquarters, US expansion, quality and standardized trailing P/E
As of November 20, 2026 Phoenix; retrieved November 21 UTC. Supplement to comparison.md; B19 #309. Research v2.

## Locations and manufacturing
Sandisk headquarters: Milpitas, California. FY2026 10-K lists US R&D/development in California, Colorado and Minnesota. All NAND wafers are made through Flash Ventures in Yokkaichi and Kitakami, Japan. No new continental-US NAND wafer fab confirmed by reviewed sources. US headquarters is not US wafer manufacturing.
SK hynix headquarters: Icheon, South Korea. Indiana West Lafayette HBM advanced packaging/testing and R&D project broke ground August 27, 2026; issuer targets customer supply second half 2029. This is a packaging/test expansion, not proof of a US front-end DRAM wafer fab. Existing Korea/China production remains relevant.

## Quality
No defensible universal highest-quality-memory winner. SK hynix has established DRAM/HBM exposure which Sandisk does not sell. Sandisk and SK hynix/Solidigm both compete in NAND/enterprise SSDs. Product comparisons require workload-specific latency, bandwidth, sustained write performance, endurance/DWPD/TBW, UBER, retention, power-loss protection, power, thermal behavior and fleet failure evidence. No comparable independent field failure/return data was verified, so no numerical reliability ranking is supported. Inference: SK hynix is the broader AI memory supplier; this does not prove lower failure rates or superior every-product performance.

## Trailing P/E standard
Use November 20 regular-session close divided by reported consolidated diluted EPS for latest completed four quarters, split/ADS adjusted. SNDK uses US GAAP; SK hynix uses K-IFRS, not identical accounting. Do not use guidance annualization in trailing column.
SNDK: independently reconstructed four-quarter GAAP EPS = (5.15 + 23.03 + 43.97 + 52.60)/8 = USD15.59375, period through October 2, 2026. At StockAnalysis observed close USD79.24: 5.0815x. Vendors report USD15.54–15.64 TTM (rounding/weighting methodology not reconciled); resulting multiple 5.07–5.10x. Sum of quarterly EPS is a practical reconstruction, not an exact recomputation of trailing weighted-average diluted shares. User historical entry USD79.15 gives 5.0758x on reconstruction. Earlier ~5.15x at USD80 aligns with TRAILING earnings, not verified forward consensus; correct previous implication that it necessarily represented annual forward EPS.
SKHY: observed November 20 close USD103.57; Yahoo vendor diluted TTM EPS USD18.07 gives 5.7316x. PROVISIONAL, USD EPS FX methodology not independently reconciled to filed K-IFRS quarterly EPS. Latest earnings through September 30, 2026. SEC prospectus confirms one ADS = one tenth ordinary common share. Local 000660 vendor P/E 4.34x is a different instrument/time/FX input and must not be substituted into US ADS comparison.
Important uncertainty: quote sources disagree on SNDK close vs historical conversation USD78.65; use identified USD79.24 web observation here, not a validated canonical FETCH price. No new market feed or canonical JSONL written; FETCH owner/runtime update not available in this session. Exact execution-clock timestamp not separately retained. No claim of current/live canonical valuation.
Latest-quarter adjusted guidance annualization ~2.8x from previous note remains RUN-RATE only; not trailing or verified fiscal-year forecast.
Both earnings denominators include reported gains; SK hynix issuer discusses Kioxia investment returns, and Sandisk release reports equity security gains. Normalized recurring earnings multiples remain unverified and may be higher.

## Sources and validation
- https://www.sandisk.com/company/office-locations
- https://investor.sandisk.com/static-files/47c2209d-7ef3-488d-b9f4-62d371ad8740 (FY2026 10-K, Aug 17 2026)
- https://www.skhynix.com/company/UI-FR-CP06/
- https://news.skhynix.com/en/indiana-groundbreaking-ceremony-sketch/ (Aug 28 2026)
- https://www.sandisk.com/company/newsroom/press-releases/2026/2026-01-29-sandisk-reports-fiscal-second-quarter-2026-financial-results
- https://www.sandisk.com/company/newsroom/press-releases/2026/2026-08-05-sandisk-reports-fiscal-fourth-quarter-2026-financial-results
- https://www.sandisk.com/company/newsroom/press-releases/2026/2026-10-29-sandisk-reports-fiscal-first-quarter-2027-financial-results
- https://stockanalysis.com/stocks/sndk/ (Nov 20 regular close, 16:00 ET)
- https://ph.investing.com/equities/sk-hynix-adr-historical-data (Nov 20 close)
- https://finance.yahoo.com/quote/SKHY/key-statistics/ (search-index snapshot; full open HTTP429; USD18.07 TTM EPS is provisional)
- https://www.sec.gov/Archives/edgar/data/2120882/000119312526299963/d32785d424b4.htm (ADS ratio)
- https://www.sec.gov/Archives/edgar/data/2120882/000119312526461909/d166755d6k.htm (consolidated nine-month diluted EPS KRW242279; no complete trailing USD reconciliation)
Validation: manual primary-source location/manufacturing review; arithmetic recomputed. No code change; no tests added. Independent quality ranking, exact SKHY TTM FX reconciliation and CI not verified.
Next action: reconcile SKHY reported TTM diluted earnings to USD with an explicit FX convention and separate nonrecurring gains for both issuers.
