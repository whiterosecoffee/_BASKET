# Marvell: adjusted-to-GAAP bridge through calendar 2028
As of November 20, 2026. USD. Reference price $125.75 at November20 19:59ET, a dated public observation rather than accepted FETCH data.

The adjusted multiple understates the price relative to modeled GAAP earnings. Under the reference assumptions, standalone FY2028 EPS is $4.60 GAAP-like versus $7.37 adjusted; FY2029 is $8.62 versus $12.60. These are conditional sensitivities, not issuer GAAP forecasts or a verified combined-company/calendar2028 estimate.

## Actual bridge
Issuer S1 reports USD millions:
- Q2: 865.9 adjusted income -326.2 SBC -214.9 acquisition amortization +3.0 restructuring gain -52.0 net contingent fair-value expense -4.5 other +36.7 tax adjustments =308.0 GAAP income. Reported EPS0.94 adjusted versus0.33 GAAP, diluted921.2M.
- H1: 1583.9 -533.8 -440.1 -5.7 -302.7 -35.8 +76.7 =342.5 GAAP income. Reported H1 EPS1.75 adjusted versus0.38 GAAP.
- Q3 issuer guidance: 1.10 adjusted EPS -0.34 SBC -0.21 amortization +0.03 tax effects -0.05 other =0.53 GAAP EPS. This is guidance for the report scheduled December1, not an actual result.

SBC is a real cost to common shareholders. Ordinary cash R&D, depreciation and ordinary financing expense remain inside adjusted earnings and are not subtracted again.

## Standalone forward sensitivities

| Fiscal period / approximate calendar proxy | Adjusted EPS input | Lower-cost modeled GAAP | Reference modeled GAAP | Higher-cost modeled GAAP | Reference GAAP P/E |
|---|---:|---:|---:|---:|---:|
| FY2028 ending January2028 / mostly CY2027 | $7.37 | $5.31 | $4.60 | $3.97 | 27.3x |
| FY2029 ending January2029 / mostly CY2028 | $12.60 | $9.67 | $8.62 | $7.66 | 14.6x |

At the reference price adjusted P/Es are17.1x and10.0x. These conditional P/Es are arithmetic, not fair-value judgments.

Reference: revenue19.84B/31.76B, diluted950M/980M, SBC10% of revenue, GAAP tax18%, adjusted-tax reconstruction11%, additional IPR&D amortization162.125M each full year (1.297B/8-year assumed life), other excluded charges100M. Lower-cost case: SBC8%, GAAP tax15%, no newly active IPR&D, other50M. Higher-cost case: SBC12%, GAAP tax21%, new IPR&D amortization216.167M (6-year assumed life), other200M. These are joint sensitivity bundles, not probability bounds. Costs may exceed the bundles.

The reference GAAP EPS increase FY2028 toFY2029 is87.3%, conditional on the strong adjusted earnings inputs. No quarterly path or growth probability is established. Additional5% shares at unchanged profit reduces EPS4.76%; it is separate from expensing SBC, which is not a second share-count charge.

## Acquisition amortization can fall, but new assets matter
S2 Note5 schedules existing amortizable-intangible expense at292.7M inFY2028 and139.6M inFY2029, versus825.4M forFY2027 (440.1M already incurred plus385.3M remaining). This runoff helps GAAP earnings catch up; it does not by itself increase adjusted earnings.

The same filing carries1.297B of indefinite-lived IPR&D, not currently amortized. It begins amortization at technological feasibility and commercial production, with expected6-to13-year lives, or is written off if abandoned. The reference case's8-year life and full-year activation are assumptions. New acquisitions, impairments, earnouts and Lumentum purchase accounting could materially change the bridge.

## Calendar and merger gates
FY2029 includes approximately February2028-January2029. It has about eleven months in calendar2028. Exact CY2028 net income =FY2029 net income -January2029 net income +January2028 net income; weighted diluted shares must also be recalculated. No annual-EPS proration is presented as exact.

S7 proposes4.5 MRVL shares per LITE share, approximate67/33 ownership, expected close1H2028 subject to approvals. The standalone sensitivities exclude LITE earnings, new shares, synergies and purchase accounting. Because closing occurs within calendar2028 if successful, these are not forecasts for actual post-deal MRVL common-share earnings.

The original merger model remains at issue189/PR191, pinned9727f90125a46fe0966c0f746a891ef2aa4cb536. Its old12.69 versus7.25 conflict is partly explained: S6's7.25 is explicitly July30 vintage, while S5's November19 normalized figure is12.73 and S4 currently shows12.60. Current aggregates converge, but basic/normalized versus diluted and standalone/deal treatment are not fully audited. The issue190 update preserves this distinction; old results remain unchanged.

## Reproduce and update
Run python calculate.py in this directory. Inputs, source classes and assumption fields live in inputs.json; results.json is generated and retains null verified-GAAP, combined and exact-calendar gates. Re-read the issuer filing and matching forecast vintages after December1. Do not add an entire new quarterly EPS result onto annual consensus; replace its expected contribution and revise subsequent guidance.

Sources S1-S7: exact URLs and source/period dates in inputs.json. This research adds no ingestion, scheduler, market runtime or shared economic engine.

