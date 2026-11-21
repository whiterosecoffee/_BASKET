# NAND contract/ASP/cost stress against SKHY recurring P/E
B19 #309 research v5, as-of Nov20 2026 Phoenix; retrieval Nov21 UTC. Continues prior comparison on branch work/309-sndk-sk-hynix-comparison. No new ingestion or shared valuation engine. This is an illustrative sensitivity of historical earnings, not a forecast.

## Conclusion
At fixed prices USD79.24 SNDK and USD103.57 SKHY, and fixed SK recurring P/E6.48594x, SNDK's5.40295x relative discount disappears if SNDK EPS falls16.697%.
With a hypothetical50% revenue share entirely price-protected, unchanged volume, costs, opex, tax/share count, this equals a24.081% drop in realized pricing of the other50%.
With two-thirds revenue protected, threshold36.122%.
These are conditional algebraic thresholds, not an empirical downside forecast or measured spot-price trigger. Public NBM coverage is by bits, not revenue; do not equate directly. Contracted pricing can still vary above floor and not all protected volume is at the current realization.

## Verified contract evidence
Official Aug13 investor-day slides:
- NBM mix ~half FY2027 BITS and ~two-thirds FY2028 BITS.
- Combination fixed/variable prices, variable portion with floors/ceilings. Non-NBM prices fluctuate with market.
- Weighted contract duration4+years; longest5.
- USD93.9B total contract value at floor prices as of agreements signed through Aug3; USD91.1B RPO including post-quarter deals. Historical dates, not current balances.
Official Oct30 filing for Oct2 quarter:
- RPO USD88.9B; approximately20% expected recognition over next12months.
- USD87.4B unbilled, USD1.5B contract liabilities.
- Off-balance-sheet collateralUSD12.8B, accessible only under specified defaults/breaches.
- Refund liabilitiesUSD1.6B primarily refundable security deposits.
Do not add TCV,RPO,collateral and deposits together as revenue/cash/profit. Do not assume every NBM has unconditional take-or-pay remedies. Guarantees are not a perpetual gross-margin floor, and customer recovery may be conditional.
The public evidence supports reduced price/volume cyclicality; it does not establish actual SKU/quarter ASP floors, protected REVENUE mix, guaranteed recoverable net profit or exact downside EPS.

## Historical base and formulas
Period: trailing four quarters through Oct2 2026. Monetary inputs USDmillions:
R=28971 = FY26 revenue20248 - FY26Q1 revenue2308 + FY27Q1 revenue11031.
C=5808 = FY26COGS5776 - FY26Q1COGS1621 + FY27Q1COGS1653.
O=2170 = FY26opex2083 - FY26Q1opex511 + FY27Q1opex598.
N=-102 = (FY26 interest/other628 - FY26Q1(-52) + FY27Q1 539) - investment gains1321.
Pretax investment-excluded P=R-C-O+N=20891.
Normalized trailing EPS14.666054308 and PE5.402952855 are estimated in investment-excluded-trailing-earnings.md. Item-specific tax effects remain estimated.

Let:
w=protected revenue weight in base-price mix (assumption, NOT known NBM bits share);
dp=protected-price change;
dm=unprotected realized-price change;
v=bit/unit volume growth;
c=unit-COGS reduction;
o=opex growth.
Then:
R_new=R*(1+v)*[w*(1+dp)+(1-w)*(1+dm)].
C_new=C*(1+v)*(1-c).
P_new=R_new-C_new-O*(1+o)+N.
EPS_new=14.666054308*(P_new/20891).
PE_new=79.24/EPS_new.
Constant tax/share count makes EPS proportional to pretax profit for this sensitivity; not an exact audited tax bridge. Baseline current EPS weighted-share adjustment and source line rounding introduce small approximation.

| Scenario | EPS change | EPS USD | PE |
|---|---:|---:|---:|
| 50% protected; market -20% | -13.9% | 12.63 | 6.27x |
| 50% protected; market -30% | -20.8% | 11.62 | 6.82x |
| 67% protected; market -30% | -13.9% | 12.63 | 6.27x |
| 50% protected; market -30%; volume +15%; unit cost -10%; opex +5% | -4.6% | 13.99 | 5.66x |
| 50% protected; contract -10%; market -30% | -27.7% | 10.60 | 7.48x |
| 50% protected; market -30%; volume -10%; unit cost flat | -29.8% | 10.29 | 7.70x |

The volume-growth row assumes15% bit growth,10% reduction in ALL modeled unit COGS,5% opex growth. These are explicit author scenario inputs, not guidance for the next quarter. Total COGS may contain fixed manufacturing costs; proportional volume scaling can understate downside when volume declines and utilization falls. Cost declines may be delayed by inventory and node ramp costs. Contract/noncontract products have different ASP and COGS; model uses a blended portfolio.
No new buyback accretion, HBF profit or contract litigation recoveries added.
At50%protected:
EPS decline=(R/P)*0.5*market_price_decline.
Break-even EPS decline=1-(5.402952855/6.485939535)=0.166974526.
Thus market decline=0.166974526*20891/(28971*0.5)=0.240810799.
If protected price drops10%, it consumes about6.93 percentage points of EPS before any noncontract decline: (28971/20891)*0.5*0.10.
Comparing against SK investment-only6.91x instead of broader financing-normalized6.49x gives more apparent cushion; use6.49x to avoid overstating SNDK advantage.

## Reconciliation to earlier 2027–2030 price illustration
Earlier EPS26/28 and15%growth at6x/7x remain conditional assumptions, not consensus or a forecast established by this model. Do not simply scale future EPS26 by historical stress ratios without rebuilding future revenue/COGS/opex and contract mix.
This model specifically tests whether the TRAILING relative discount is robust to repricing; it does not validate a doubling or tripling scenario. Equal gross TAM growth does not establish equal EPS growth.
Competitive interpretation: SNDK can keep relative value despite a moderate unprotected ASP drop, provided contracted realization and bit/efficiency growth hold. SK breadth offers more buffers from HBM/DRAM when NAND weakens, but SK EPS itself is not modeled flat as a claim—flat SK is a benchmark assumption.

## Additional current-quarter evidence
Oct2 10-Q describes total products sold up almost10% in exabytes YoY, while datacenter exabytes up almost330%, Edge exabytes down20% and Consumer exabytes down more than70%. This shows pricing and MIX were material earnings drivers; headline revenue growth is not pure physical volume growth. These are issuer statements, not independent measurements.
Improving manufacturing density/bandwidth is useful technical evidence; do not translate wafer density gain directly into percentage cost savings or finished-product yield improvement.

## Sources
1. https://investor.sandisk.com/static-files/c050c0a0-91fe-4186-bb34-3b331378060f (Aug13 investor-day slides, contract mechanisms and bit coverage).
2. https://investor.sandisk.com/static-files/c31aa9f9-d8e1-43e5-8642-360f5d0dad15 (Oct30 10-Q, Oct2 end period; Notes4 and MD&A).
3. https://www.sandisk.com/company/newsroom/press-releases/2026/2026-08-05-sandisk-reports-fiscal-fourth-quarter-2026-financial-results (FY26 financial base).
4. https://www.sandisk.com/company/newsroom/press-releases/2026/2026-10-29-sandisk-reports-fiscal-first-quarter-2027-financial-results (FY27Q1 and comparable FY26Q1).
Prices and SK normalization sources retained in earlier reports. No current FETCH refresh claimed. External search result for Micron strategic agreements was excluded as wrong issuer; Micron contract assertions must not be attributed to Sandisk.

## Review and next action
JS arithmetic executed with six scenarios and both break-even weights. Source classification and bits/revenue distinction manually reviewed. No production implementation/tests or independently verified CI. Missing price floors, protected revenue mix, fixed/variable fab costs, node yield curve and contract recoverability prevent a verified downside probability or precise fair value.
Next: reconcile protected revenue mix from NBM billing/recognition disclosures and product realization; if unavailable, retain50–67% as sensitivities rather than promote to verified inputs.
