# December 2028 reverse valuation — November 21, 2026

Decision: no qualified rotation. Existing FETCH #152 remains unacknowledged; historical Nov20 closes from the pinned snapshot only. Relevant PR307/308/310/313/292/191 heads unchanged on recheck. This child adds useful required outcomes without inventing forecasts. No change to the 60 unqualified forward rows.

A 50% price gain by December 31, 2028 requires the following. Exit multiples are arithmetic sensitivity columns, not justified common multiples. Dividends and friction are zero in this illustration; actual total wealth must include eligible dividends and costs.

|Core|Historical price|Required terminal price|Required EPS at 20x|At 30x|At 40x|Annual economic FCF/share at 5% terminal yield|
|---|---:|---:|---:|---:|---:|---:|
|NVDA|$125.53|$188.30|$9.41|$6.28|$4.71|$9.41|
|AMD|$424.39|$636.59|$31.83|$21.22|$15.91|$31.83|
|INTC|$51.28|$76.92|$3.85|$2.56|$1.92|$3.85|
|AVGO|$304.41|$456.62|$22.83|$15.22|$11.42|$22.83|
|MRVL|$122.28|$183.42|$9.17|$6.11|$4.59|$9.17|

Required EPS = P0*(1+price return)/exit PE. Required annual economic FCF/share = terminal price*terminal FCF yield. The cash column is a separate valuation cross-check, not a conversion forecast. P/E can fail for Intel's foundry losses or transaction-distorted MRVL; require segment/FCF cross-checks before admitting either. The accompanying JSON includes flat/50%/100% target returns at all three multiples (45 rows).

## What changes the pair answer

With zero dividends, AVGO→MRVL at the historical ratio 2.489450 and a 10% gross relative hurdle requires EPS_AVGO/EPS_MRVL ≤ 2.263137*(PE_MRVL/PE_AVGO). At AVGO30x and MRVL35x this bound is 2.640326; at AVGO35x and MRVL25x it is 1.616526. These multiples are sensitivities, not justified exits. A sufficiently large multiple haircut alone can reverse the apparent growth advantage.

NVDA→AMD similarly requires EPS_NVDA/EPS_AMD ≤ .268899*(PE_AMD/PE_NVDA). At NVDA30x/AMD40x the bound is .358532; at NVDA35x/AMD25x it is .192071. Same-regime EPS, margins, share counts and cash must validate the chosen multiple. No switch or ranking is admitted by this algebra alone.

A 20% exit-multiple haircut requires 25% higher EPS to preserve the same terminal price. A simultaneous 20% EPS miss and 20% multiple haircut reduces modeled equity price by 36%. A forecast at a switch boundary has no revision cushion; the shared vector must quantify that cushion before promotion.

## Qualification tests

NVDA: reconcile accelerator/networking/system gross versus net content, equity gains, recurring taxes and retained SBC. AMD: qualify EPYC/Instinct operating profit, software deployment and warrants/dilution. INTC: eliminate internal foundry transfers, reconcile JV/lease/fab funding and depreciation. AVGO: include VMware cash and issuer-specific segment multiples; retain SBC and ordinary R&D. MRVL: retain SBC, amortization variants and acquisition costs; use post-close diluted shares only in a conditional close case and avoid double counting Celestial.

No quarter is multiplied by four and labeled a forecast. No annual or cumulative EPS growth is computed against an unqualified baseline. No execution, monitoring or predictive performance is claimed.

Next action: qualify the AVGO/MRVL December2028 recurring earnings/cash/share vector from existing owner packets, with reported, conditional-close and break views. FETCH receipt remains independently required for an executable index.
