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
