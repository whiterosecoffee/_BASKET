# AVGO annual and cumulative EPS growth
As of November 20, 2026 America/Phoenix. USD, normalized/adjusted analyst estimates; FY2026 is estimated, not reported. Fiscal years end around late October/early November; future exact dates and report dates are not confirmed.

| FY | EPS | YoY | Cumulative vs FY2026 | P/E at $304.41 |
|---|---:|---:|---:|---:|
| 2026 | $11.78 | — | 0.0% | 25.8x |
| 2027 | $19.62 | 66.6% | 66.6% | 15.5x |
| 2028 | $30.61 | 56.0% | 159.8% | 9.9x |
| 2029 | $41.48 | 35.5% | 252.1% | 7.3x |
| 2030 | $48.63 | 17.2% | 312.8% | 6.3x |

EPS grows 4.13x across FY2026–2030 (~42.5% CAGR). This is earnings growth, not a stock return. Constant-price P/E does not forecast the future market multiple.

## Valuation sensitivity
Hypothetical 20x/25x same-year EPS values: FY2027 $392/$491; FY2028 $612/$765; FY2029 $830/$1,037; FY2030 $973/$1,216. These are undiscounted arithmetic scenarios, not fair values, targets or probabilities. At FY2028 EPS cut 25% ($22.9575) and 15x, value is $344.36 (+13.1% vs close); a 40% cut and 12x gives $220.39 (-27.6%). Dividends, tax and execution costs excluded.

## Evidence and risks
Primary annual EPS series: https://www.chartmill.com/stock/quote/AVGO/estimates (search-index capture, direct fetch 403). Reuses #291 series, adding FY2030 $48.63. Alternative November19 Kaplio series is $11.68/$19.32/$30.71; keep separate.
Price: https://stockanalysis.com/stocks/avgo/ closing $304.41 November20 4pm ET; AH $310.89 7:34pm ET, historical references not live quotes.
Issuer: https://investors.broadcom.com/news-releases/news-release-details/broadcom-inc-announces-third-quarter-fiscal-year-2026-financial . Q3 revenue $29.6B, AI revenue $16.7B; Q4 issuer AI revenue outlook $21.7B. Custom AI accelerators/networking underpin growth; infrastructure software adds diversification. Q3 GAAP EPS $2.68 vs adjusted $3.32. Adjustments include stock compensation and intangible amortization; future GAAP EPS not modeled.
Reported risk: https://www.barrons.com/articles/broadcom-stock-google-ai-chips-e75d888d . Kuo survey reportedly cuts Google 2027 Broadcom-designed TPU series volumes 20%; neither issuer confirmed in this source. Not a 20% total AVGO revenue cut. Supplier/model mapping has conflicting reports; do not record canonical edges from this survey. Consensus may predate this report. Competitive design shifts, customer concentration, power/packaging constraints and earnings revisions are thesis risks. 2029–2030 coverage is sparse and cross-metric margins/cohorts are not reconciled; avoid claiming a full operating model.

## Review and next action
All 98 open PR file inventories checked before claiming scope; none overlaps this new AVGO path. Arithmetic calculated in JavaScript and reviewed using growth-factor identities. No new runtime, FETCH, canonical quote/JSONL writer, independently certified feed, backtest, probability, merge or release. Canonical B02/B03 qualification and exact-head hosted CI remain pending. Next: reconcile customer-specific TPU exposure and updated FY2027 EPS after issuer commentary.

## Competitive moat: AVGO versus MRVL + Celestial AI + proposed Lumentum
Research date November20,2026. CEL interpreted as Celestial AI; if user means Celestica (CLS), it is a different system-integration layer.

Transaction status: Celestial acquisition closed February2,2026; Lumentum agreement announced November2 with expected H1calendar2028 close, subject to approvals. Current announcement ratio4.500 MRVL/LITE, not historical user5.5. Do not assume completed LITE integration or sum standalone EPS.

Qualitative inference, not measured market-share ranking:
- AVGO advantage today: mature merchant switch/CPO integration, switch SDK and system qualification, manufacturing/test/thermal/connector ecosystem and customer design experience. Not dependent on copper remaining dominant.
- MRVL+Celestial threat: optical scale-up and package-level XPU chiplets; Photonic Fabric could secure valuable design wins at a new architectural boundary. Company performance claims are not independently benchmarked.
- Proposed LITE integration: InP/lasers/optical manufacturing plus electrical DSP/custom-silicon co-design could improve control over cost, yield and timing. This is an intended post-close benefit, not delivered group-wide evidence.
- Broadcom also develops lasers/photodetectors, CPO, near-packaged optics and custom-XPU packaging; avoid falsely characterizing it as only a copper/switch supplier.
- Switching cost operates at qualified architecture/product cycle; hyperscalers can dual-source or redirect the next generation. Open standards expand adoption and also permit competition. No permanent proprietary monopoly established.
- More components under one owner do not ensure better power, yield, serviceability or customer neutrality. A MRVL/LITE group may face customer/channel conflicts while AVGO also has powerful concentrated buyers.
- MRVL/Celestial optical IO can coexist with Broadcom Ethernet switching. A connection win does not imply displacement of the entire fabric or processor logic.
- Celestica DS6005 explicitly uses Broadcom TH6-Davisson; CLS system integration is not Celestial chiplet IP.

Timing: Celestial company roadmap initial revenue H2FY2028 (~second half calendar2027), $500M annualized Q4FY2028 (~Jan2028), $1B annualized Q4FY2029 (~Jan2029); not annual booked revenues. LITE expected H1calendar2028 close then integration. Treat 2027 execution and 2028–2030 architecture competition separately.

Investment implication: demonstrated AVGO execution supports higher earnings confidence than an uncompleted combined roadmap, but cannot independently justify forecast EPS/multiples. Threat needs measured share/ASP/margin sensitivity; no arbitrary automatic haircut to all AVGO revenue. Monitor named shipping XPU designs, recurring revenue, independent power/latency/error-rate comparison at matched reach/temperature, packaging yield and field repairability, and diluted EPS after integration. Broadcom moat weakens if repeat high-volume sockets move away while its pricing/margins erode.

Primary sources:
https://investor.marvell.com/sec-filings/all-sec-filings/content/0001193125-26-442714/d81187dex991.htm
https://www.marvell.com/company/newsroom/marvell-completes-acquisition-of-celestial-ai.html
https://investor.marvell.com/news-events/press-releases/detail/1000/marvell-to-acquire-celestial-ai-accelerating-scale-up-connectivity-for-next-generation-data-centers
https://investors.broadcom.com/news-releases/news-release-details/broadcom-announces-third-generation-co-packaged-optics-cpo
https://investors.broadcom.com/news-releases/news-release-details/broadcom-showcases-industry-leading-solutions-scaling-ai
https://celestica.gcs-web.com/node/17831/pdf
Reused existing qualitative research: PR191 head0928564c9a0a83e6223b60bdacdc51dec9154b24 research/models/mrvl_lite/optical_competition_2026-11-20.json (read only).

## Customer and margin stress
All scenario inputs hypothetical; not known customer exposure or updated consensus. Revenue references178.513B/287.345B; EPS19.62/30.61. Assume65% contribution on lost revenue,16% marginal tax,5B shares, incremental margin shock on remaining revenue.
| Case | Revenue loss | Extra margin pressure | Extra dilution | FY27 EPS | FY28 EPS | FY28 value at15x |
|---|---:|---:|---:|---:|---:|---:|
|Estimate baseline|0%|0pp|0%|19.62|30.61|459.15|
|Narrow product cut|4%|0pp|0%|18.84|29.35|440.32|
|Broader pressure|6%|3pp|0%|17.60|27.37|410.49|
|Severe competition|12%|5pp|2%|15.65|24.24|363.54|
These cases preserve much of the original growth path: not an exhaustive downside range. One-year delay: FY28 EPS19.62 at15x=$294.30. Severe-case FY28 at12x=$290.83. At15x FY28 break-even EPS vs prior304.41 close is20.294,33.7% below baseline. Full model fields/formula in inputs-results.json.
Issuer confirms December9,2026 after-market FY2026 report: https://investors.broadcom.com/news-releases/news-release-details/broadcom-inc-announce-fourth-quarter-and-fiscal-year-2026

## Google relationship and stress interpretation — November20,2026
Google matters as a TPU co-development/supply and AI networking customer/partner, not because a verified equity stake controls Broadcom. April6 SEC8-K confirms future-generation custom TPU development/supply and networking/other rack components through up to2031; a separate Anthropic collaboration provides access through Broadcom to approximately3.5GW beginning2027, contingent on Anthropic commercial success. This filing does not disclose per-generation purchase minimums, economics, exclusivity or a guaranteed profit stream.
Source https://www.sec.gov/Archives/edgar/data/1730168/000119312526144028/d87999d8k.htm

Ownership: no strategic Alphabet/Google AVGO equity investment established by reviewed sources. Broadcom2026 proxy as-of-Feb24 >5% owner table names Vanguard9.9% and BlackRock7.3%, not Alphabet. It cannot rule out smaller holdings or later changes; do not claim zero ownership as verified current fact.
Source https://www.sec.gov/Archives/edgar/data/1730168/000119312526085691/d49254ddef14a.htm

Concentration: August2 quarter top-five end customers55% aggregate; one direct distributor50%. Neither statistic identifies Google's revenue share; do not label unnamed distributor as Google.
Source https://www.sec.gov/Archives/edgar/data/1730168/000173016826000080/avgo-20260802.htm

Meaning of Google customer-share loss: reduced share of Google's chip procurement allocated to AVGO, product mix/ASP changes or deployment delays. Those can occur while total AI demand grows. Existing20/30/40% affected revenue shares in stress model are hypothetical total-company product exposures, not verified Google percentages. Example20% exposure x20% product-sales reduction =4% total revenue loss under constant ASP; premium-product mix could magnify it.
Stress results remain baseline19.62/30.61 FY27/FY28; narrow4% revenue loss18.84/29.35; broader6% loss+3pp additional operating-margin compression17.60/27.37; severe12% loss+5pp compression+2%dilution15.65/24.24. Assumptions65% lost-revenue contribution,16% tax,5B diluted shares; not company guidance, GAAP EPS or calibrated probabilities. If baseline growth stalls, downside can exceed these preserved-growth cases.
Each additional1pp margin compression on full baseline sales costs about0.30FY27EPS and0.48FY28EPS under the same tax/share assumptions. Long-term relationship provides visibility; earnings durability still depends on allocated content, volumes, pricing, costs and dilution.

## AVGO versus MRVL/LITE: trailing valuation and future growth — November20,2026
Regular-session close reference USD: AVGO304.41, MRVL122.28,LITE460.54. Provider trailing GAAP P/E38.86,41.08,not meaningful respectively. Published rounded EPS7.83,2.98,-82.08; use provider unrounded multiples rather than imply precision by dividing rounded fields. Source stockanalysis.com/stocks/{avgo,mrvl,lite}/ accessed this turn.
MRVL trailing earnings include a1.8B pretax automotive Ethernet divestiture gain (completed Aug14,2025; last reported quarter Aug2026 means gain remains in trailing period). Source https://investor.marvell.com/news-events/press-releases/detail/999/marvell-technology-inc-reports-third-quarter-of-fiscal-year-2026-financial-results . Do not treat trailing GAAP PE as recurring operating valuation. LITE debt extinguishment materially distorts GAAP losses; source https://www.sec.gov/Archives/edgar/data/1633978/000162828026057358/lite-20260627.htm .
Simple sum of displayed company TTM income2.64B-6.58B=-3.94B; combined trailing GAAP PE not meaningful. This is a diagnostic of reported historical earnings, not a transaction-adjusted pro forma statement or average of PEs.

Future estimates: ChartMill single-provider normalized EPS per issuer. MRVL/LITE snapshot recorded Nov14; AVGO captured Nov20 without independently verified original update time. No qualified live canonical feed, FETCH or ticker store used. All valuation prices dated Nov20 close.
https://www.chartmill.com/stock/quote/AVGO/estimates
https://www.chartmill.com/stock/quote/MRVL/estimates
https://www.chartmill.com/stock/quote/LITE/estimates

|Issuer|FY end approximately|EPS|YoY growth|Cumulative vs own FY26|P/E at Nov20 close|
|---|---|---:|---:|---:|---:|
|AVGO|Oct/Nov 2026|11.78|—|0.0%|25.8x|
|AVGO|Oct/Nov 2027|19.62|66.6%|66.6%|15.5x|
|AVGO|Oct/Nov 2028|30.61|56.0%|159.8%|9.9x|
|AVGO|Oct/Nov 2029|41.48|35.5%|252.1%|7.3x|
|AVGO|Oct/Nov 2030|48.63|17.2%|312.8%|6.3x|
|MRVL|Jan 2026|2.85|—|0.0%|42.9x|
|MRVL|Jan 2027|4.30|50.9%|50.9%|28.4x|
|MRVL|Jan 2028|7.51|74.7%|163.5%|16.3x|
|MRVL|Jan 2029|13.03|73.5%|357.2%|9.4x|
|MRVL|Jan 2030|14.76|13.3%|417.9%|8.3x|
|LITE|Jun 2026|8.37|—|0.0%|55.0x|
|LITE|Jun 2027|24.21|189.2%|189.2%|19.0x|
|LITE|Jun 2028|39.70|64.0%|374.3%|11.6x|
|LITE|Jun 2029|54.95|38.4%|556.5%|8.4x|
|LITE|Jun 2030|unverified|—|—|—|

Fiscal periods are NOT aligned. MRVL FY2028 ends Jan2028, LITE Jun2028, AVGO around Nov2028. Their FY26 baselines similarly differ; cumulative growth percentages do not span identical dates. For endpoints clustered near calendar2028 year-end: AVGO FY28 Nov28 EPS30.61(+56.0% YoY,+159.8% vs FY26), MRVL FY29 Jan29 EPS13.03(+73.5%,+357.2%), LITE FY29 Jun29 EPS54.95(+38.4%,+556.5%); LITE extends7months beyond AVGO. This approximate overlay is not exact calendarization.

Pairing status: LITE transaction remains proposed, expected H1calendar2028. Cannot add standalone EPS, average PEs, stack Celestial expected revenue atop embedded consensus, or label constituent growth as combined-parent EPS. Proper combined formula: (calendar-aligned MRVL earnings + aligned LITE earnings + after-tax synergies - integration/purchase-accounting adjustments)/(MRVL diluted shares + 4.5*eligible LITE shares + other incremental dilution), after avoiding preexisting earnings adjustments/double count. Preclose holding mix unspecified; no invented portfolio weights. Existing owner PR191 research remains read only.
LITE2030 null; do not extrapolate a consensus. MRVL2030 EPS rises while provider sales/operating income decline; sparse/different analyst-cohort inconsistency unresolved. Distant forecasts not a verified integrated model.

Interpretation: AVGO lower published trailing multiple and lower own-FY28 normalized multiple than either constituent; MRVL/LITE show faster long-horizon earnings growth but carry calendar, concentration, dilution and integration uncertainty. No universal risk-adjusted winner established. Next: calendarize combined diluted earnings to common Dec2027/Dec2028 endpoints before parent valuation.

## Competitive paths and combined MRVL+ share prices
Model: competitive-paths-2030.json. Illustrative normalized economics, not consensus/targets/probabilities. USD billions except EPS/prices; MRVL+ combines external MRVL/LITE revenue with intercompany eliminations and merger shares, including existing Celestial once. Conditional on deal. Calendar2027 combined earnings are hypothetical preclose pro forma.
Material update: official Oct6 investor deck targets standalone MRVL FY2031 (aroundJan2031) revenue70–90B, adjusted EPS>30, opmargin44–46%, tax15%. Prior sparse FY2030 EPS14.76 cannot be treated as definitive current trajectory. It is not combined diluted EPS or a guaranteed result.

|Scenario|AVGO revenue growth FY27/28/29/30|AVGO2030 revenue|AVGO2030 R&D|AVGO2030 opmargin|MRVL+2030 revenue|MRVL+2030 R&D|MRVL+2030 opmargin|
|---|---|---:|---:|---:|---:|---:|---:|
|AVGO maintains lead|60%/55%/25%/20%|394.3|35.5 (9%)|63%|45|7.2 (16%)|33%|
|Competitive convergence|50%/40%/20%/15%|307.2|36.9 (12%)|58%|70|9.8 (14%)|40%|
|Meaningful AVGO share loss|40%/25%/12%/10%|228.5|34.3 (15%)|51%|100|12.0 (12%)|44%|

|MRVL+ calendar year|AVGO maintains lead,18x|Convergence,24x|AVGO share loss,25x|
|---|---:|---:|---:|
|2027|$88 (-28%)|$147 (+20%)|$182 (+49%)|
|2028|$114 (-7%)|$226 (+84%)|$310 (+154%)|
|2029|$133 (+9%)|$303 (+148%)|$461 (+277%)|
|2030|$146 (+19%)|$380 (+210%)|$630 (+415%)|
Price returns are cumulative vs122.28 entry reference, not cumulative EPS percentages.

|AVGO fiscal year|Maintains lead,20x|Convergence,18x|Share loss,15x|
|---|---:|---:|---:|
|2027|$353|$292|$220|
|2028|$541|$395|$257|
|2029|$664|$455|$267|
|2030|$774|$497|$269|
AVGO fiscal-year endpoints aroundNov vs MRVL+ modeled calendar-yearDec. Revenue base106B FY2026 is a rounded research estimate, not filed actual. Gross margins/R&D split and future tax/interest/shares are explicit scenario choices. AVGO maintains-lead EPS2030$38.70 is below earlier consensus48.63 because this model independently assumes slower revenue ramp and more conservative earnings economics; not a verified consensus revision.
MRVL+ EPS2030$8.11/$15.81/$25.19; shares1.4B. EPS is normalized with no GAAP SBC/amortization/integration cash-cost bridge; not owner earnings. 2030 values$146/$380/$630:1.19x/3.10x/5.15x current MRVL reference.
4x target489.12 requires EPS24.46at20x,19.56at25x,16.30at30x; at40%opmargin18%tax1B netfinancing1.4B shares, required revenue106.9B/86.0B/72.1B. ~40%annualized share-price return for roughly4years, no probability implied.
Synergy sensitivity:1B pre-tax improvement net of implementation at18%tax/1.4B shares adds0.586EPS (~14.64/share at25x); no double addition because margins already embed synergy. 3pp lower opmargin on70B revenue reduces EPS1.23 (~29.40/share at24x). 10%extra shares reduces EPS/value9.1% holding earnings/multiple fixed.

MRVL+ headwinds: AVGO R&D budget remains~34–37B even under competitive pressure versus MRVL+7–12B, so competitor can fund a sustained response; illustration, not measured R&D budgets. Customers can resist vertical bundles or dual-source; ownership of LITE may create neutrality/channel conflicts. Yield/thermal/repairability determine production adoption; a failure in one tightly integrated stage can delay whole platforms. Laser fabs add capital demands and working capital beyond fabless engineering. CPO can cannibalize discrete DSP/pluggable content; eliminate internal sales. Differentiated ASIC supply does not guarantee software lock-in or permanent margins. Shares, earnouts, talent costs, SBC, integration and purchase accounting matter. Industry/NVDA/other competition remains; profits are not a two-company zero-sum pool.
4x is economically feasible under strong delivery plus retained premium valuation. It is not automatic from acquiring LITE or4x corporate revenue; middle case here~3.1x, bull~5.1x. No unsupported odds.

Sources: official October6 Marvell investor deck and Nov2 merger presentation linked in model. Company targets distinct from our assumptions. Readback/JavaScript arithmetic validation only; hosted exact-head CI and independent review pending.

## User-standardized AVGO $300 baseline and common December endpoints
User entry assumption300AVGO; research snapshotNov20,2026. Original normalized EPS series11.78/19.62/30.61/41.48/48.63 converted at unchanged25.466893xFY26E earnings.
|FY|EPS|YoY|Cumulative vsFY26|Price at fixed multiple|
|---|---:|---:|---:|---:|
|2026|11.78|—|0.0%|300.00|
|2027|19.62|66.6%|66.6%|499.66|
|2028|30.61|56.0%|159.8%|779.54|
|2029|41.48|35.5%|252.1%|1056.37|
|2030|48.63|17.2%|312.8%|1238.46|
This is a mechanical conversion of EPS estimates, not price consensus or a share-price forecast. Original EPS estimate dates/sparse coverage caveats preserved. FY dates end around lateOct/earlyNov, notDec31. At2030EPS48.63,20x=$972.60 and15x=$729.45. It differs from earlier competitive-path price scenarios because that separate model changes revenue, margins, diluted EPS and terminal multiple.

Common December comparison: starting investment300each,1AVGOat300 vs300/122.28=2.453385672MRVL shares. MRVL+ is conditional pro-forma combined parent, not a second LITE position. In2027parentisnotyetclosed; values are hypothetical combined economic sensitivities rather than actual standaloneEPS valuation. AVGOcalendarEPSapprox10/12currentFY+2/12followingFY, smooth earnings assumption, not exact quarterly calendarization. MRVL+ annual endpoints were modeled calendar years. Both comparison and constant-multiple series are stored in competitive-paths-2030.json.
|Scenario|Dec2027 AVGO|Dec2027 MRVL+ investment|Dec2028 AVGO|Dec2028 MRVL+ investment|
|---|---:|---:|---:|---:|
|AVGO maintains lead|384.43|216.19|561.41|280.11|
|Competitive convergence|308.72|359.96|404.70|553.48|
|Meaningful AVGO share loss|226.06|445.89|258.69|761.07|
All investment values USD; do not label MRVL standardized capital value as its actual share price. Dividends/tax/costs excluded.

## Multiple durability and explicit compression path
Research snapshotNov20,2026. Judgment:25x adjusted earnings can be a premium scenario, but is not established fair value. Condition on sustained per-share growth, cash conversion after economic stock compensation, retained customer sockets, pricing and returns on incremental R&D. As growth slows, reduce modeled P/E rather than assume immutable premium.
Newly retrieved ChartMill annual table keeps EPS11.78/19.62/30.61/41.48/48.63/53.19 throughFY2031 (2031growth9.4%). Original estimate snapshot latestFY2026 observationNov14. Primary source companyQ3 release cashflow13.665B and GAAPEPS2.68vsadjusted3.32; stock compensation excluded from adjustedEPS.2026Q3stockcomp2.019B from10-Q. FCF is not equivalent to economic owner earnings after dilution.
Provider quality warning: ChartMill FY2029 operating margin74.2% exceeds listed gross margin70.2%; FY2030operating72.7% exceeds gross70.5%. Metrics are not a reconciled same-basis operating model. Do not promote its standaloneEPS series into verified profitability or reliable2030fair value; analyst-cohort/accounting-basis reconciliation needed. Preserve evidence rather than overwrite series.
Source https://www.chartmill.com/stock/quote/AVGO/estimates
Source https://investors.broadcom.com/news-releases/news-release-details/broadcom-inc-announces-third-quarter-fiscal-year-2026-financial
Source https://www.sec.gov/Archives/edgar/data/1730168/000173016826000080/avgo-20260802.htm
Compression sensitivity:assumeFY27/28/29/30sameyearadjustedP/E24/22/20/18, no empirical probability or fair-value claim.
|FY|EPS|AssumedPE|Price|Cumulative return from300|
|---|---:|---:|---:|---:|
|2027|19.62|24|470.88|57.0%|
|2028|30.61|22|673.42|124.5%|
|2029|41.48|20|829.60|176.5%|
|2030|48.63|18|875.34|191.8%|
2030EPS25%below48.63and15x=$547.0875,+82.36%from300. Not a downside floor; deeper earnings/multiple declines can lose capital. No dividends/tax/costs, discounting or current-price claim. Next action: reconcile distantEPS with common-basis margins and diluted FCF before investment-grade target claims.
