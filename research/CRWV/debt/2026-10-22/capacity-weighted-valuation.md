# CRWV quarterly capacity model and subjective scenario weighting

October 22, 2026. USD throughout. B10 #68 / draft PR #69. This conditional expansion-demand model supplements, rather than silently replaces, the earlier guidance-anchored valuation. Higher values result from different explicit deployment and realized-price assumptions, not newly reported actual earnings.

## Current capacity and historical quarterly additions

Latest independently retrieved consolidated actual: approximately **1.5GW at June 30, 2026**. CoreWeave's current facility webpage still displays that footprint; it is not a fresh October measurement. August contracted power was approximately 4.2GW. End-2026 target is >1.85GW active power. September-quarter actual active power was not found in retrieved company disclosures. The actual October total is unknown; no interpolated number is labeled current fact.

| Quarter-end | Active power | Approximate addition |
|---|---:|---:|
| Q4 2024 | >360MW | Baseline |
| Q1 2025 | 420MW | ~60MW |
| Q2 2025 | 470MW | ~50MW |
| Q3 2025 | 590MW | ~120MW |
| Q4 2025 | >850MW | ~260MW |
| Q1 2026 | >1,000MW | ~150MW; rounded bounds |
| Q2 2026 | ~1,500MW | Nearly 500MW |
| Q3 2026 | Not verified | Not verified |
| Q4 2026 | >1,850MW target | >350MW across H2, not a disclosed Q3/Q4 split |

Sources: quarterly issuer releases at https://investors.coreweave.com/financials/quarterly-results/ and https://www.coreweave.com/ai-data-centers . Q1/Q2 2025 releases, Q3 2025 release, FY2025 release, Q1/Q2 2026 releases reviewed directly. Rounded bounds prevent exact subtraction claims.

Capacity growth is visibly accelerating in several periods, but a few lumpy additions do not estimate a stable exponential law. Revenue equals the time integral of billable MW times realized revenue/MW, not quarter-end capacity multiplied by a full year's price. An accelerating installation schedule can produce strongly convex annual revenue without an unrestricted exponential extrapolation.

## Utilization and pricing assumptions

The user requests **100% utilization**; model this as every MW earning immediately once ready to bill. No vacancy haircut is applied. Construction/acceptance dates remain relevant: buildings do not earn before hardware/service readiness. The model treats future capacity inputs as billable IT-comparable capacity; the mapping from company active-power definitions and selected cluster-pricing MW is not independently reconciled. A gross-facility/IT mismatch would overstate revenue.

NVIDIA's disclosed residual-capacity arrangement has delivery/availability conditions. Full utilization here is a user-directed scenario, not a claim that NVIDIA guarantees all future MW or peak prices.
https://www.sec.gov/Archives/edgar/data/1769628/000176962825000047/crwv-20250909.htm

The strongest price anchor is CoreWeave's own September 17 release: selected 3–6-month contracts at **~$40M/MW annualized**. SpaceX-related $30–50M/MW/year is treated as a proposed pricing range, not verified identical economics. It cannot all be imposed on existing fixed contracts. At 1.85GW, management's $19B exit-2026 midpoint corresponds to approximately $10.27M/MW/year across the fleet; that contrast requires a mix/tenor bridge.
https://investors.coreweave.com/news/news-details/2026/CoreWeave-Continues-to-Contract-New-Compute-Capacity-at-Higher-Prices/default.aspx

Hold the end-2026 fleet's annual revenue at $19B. For capacity added after that point, model these blended realized yields, USD millions/MW/year (numerically equal to USD billions/GW/year):

| Case | 2027 new-capacity yield | 2028 new-capacity yield | Interpretation |
|---|---:|---:|---|
| Slow | 15 | 15 | Lower premium participation, older/cheaper mix |
| Base | 19 | 17 | 2027 example: 25% at $40M and 75% at $12M; 2028 repricing/mix moderates |
| Bull | 28 | 20 | 2027 example: ~39% at $50M and remaining at $14M; 2028 premium normalizes |

These mixes are assumptions, not disclosed allocations. Full utilization and price normalization are compatible. The unchanged legacy revenue is conservative on renewals; separate recurring software/services valuation is not added. All revenues, including later contracts, are consolidated within this yield formulation.

For comparison only, 3GW all earning $30–50M/MW/year would generate $90–150B annually. That requires a fleet-wide realized price and service boundary not established by the selected short-term contract disclosure. It is a mathematical ceiling scenario, not the central forecast or evidence that the old backlog can be accelerated contractually.

## Quarterly billable-capacity scenarios, not company guidance

| End quarter | Slow GW | Base GW | Bull GW | Base addition MW |
|---|---:|---:|---:|---:|
| Q4 2026 starting assumption | 1.85 | 1.85 | 1.85 | — |
| Q1 2027 | 1.95 | 2.05 | 2.15 | 200 |
| Q2 2027 | 2.10 | 2.30 | 2.50 | 250 |
| Q3 2027 | 2.25 | 2.65 | 3.00 | 350 |
| Q4 2027 | 2.40 | 3.00 | 3.60 | 350 |
| Q1 2028 | 2.55 | 3.25 | 3.90 | 250 |
| Q2 2028 | 2.70 | 3.50 | 4.20 | 250 |
| Q3 2028 | 2.85 | 3.75 | 4.50 | 250 |
| Q4 2028 | 3.00 | 4.00 | 4.80 | 250 |

The site evidence in capacity-conversion.md supports a multi-site rollout but does not certify these exact quarterly totals. Base keeps 2028 end capacity below the August 4.2GW contracted total, although not every contracted tranche's exact delivery date is verified. Bull requires additional firm capacity beyond that dated contracted total. Neither assumes all available powered land is ready now.

## Expense and funding model

Reproducible script: capacity-scenarios.py. Numeric results: capacity-scenarios.json. Each quarter uses average beginning/end capacity, modeling additions at midquarter. Formula: quarterly revenue = [19 + (average GW - 1.85) x new-capacity yield] / 4.

Common assumed end-2026 balance: $50B funded debt, $3B available cash, 600M economic shares. These are **scenario starting balances, not reported October balances or a reconstructed capitalization table**. Legacy annual D&A $9B; new equipment depreciated over six years; no life extension in the central result. The initial legacy D&A is not an independently assembled asset-cohort schedule.

| Assumption | Slow | Base | Bull |
|---|---:|---:|---:|
| Equipment/fitout cost per incremental MW | $30M | $35M | $40M |
| Operating EBITDA margin after stock compensation | 60% | 64% | 66% |
| Blended financing cost | 9.0% | 7.5% | 6.5% |
| Assumed price for new equity and SBC shares | $60 | $100 | $150 |

Margins include rent/power/direct operating costs, corporate overhead and SBC. They are assumptions of mature contribution, not current reported margins. Equipment price differences reflect scenario hardware mix; costs are not verified vendor quotes. At the base 2027 addition of 1.15GW, $35M/MW implies $40.25B incremental capex. New debt funds 80% of equipment cost and amortizes over five years. Initial $50B debt is approximated as repaying $10B annually; this is a simplified funded-debt runoff, not the actual instrument maturity ladder. Interest applies to average modeled debt; no separate capitalized-interest benefit is claimed.

Cash profit funds principal and the remaining 20% capex; any modeled shortfall issues equity. Stock compensation is 3% of revenue, already expensed in the margin, added back for cash funding and issued as shares at the scenario issue price. Taxes are 20% on positive quarterly pretax profit, with no tax benefit assumed for losses. Economic EPS uses quarterly-average shares. Convertible interest is not added back; an exact GAAP if-converted calculation is not attempted. Missing explicit variables include cash timing/prepayments, working-capital changes, restricted reserves, refinancing fees, exact future vendor terms, asset retirements and separate maintenance/replacement capex beyond that embedded in operating costs; actual funding needs can differ materially. This is an operating/funding sensitivity, not a complete FCFE DCF.

## Results and subjective weights

| Metric | Slow | Base | Bull |
|---|---:|---:|---:|
| Subjective weight | 30% | 50% | 20% |
| 2027 revenue | $22.84B | $28.62B | $39.83B |
| 2028 revenue | $31.75B | $47.05B | $66.00B |
| 2027 economic EPS | -$1.87 | $2.59 | $10.38 |
| 2028 economic EPS | $1.30 | $7.17 | $15.53 |
| 2028 selected P/E | 18x | 24x | 26x |
| October 2027 valuation | $20 | $150 | $353 |
| Present equivalent | $18 | $134 | $315 |

Discount end-2028 P/E values by 1.2 years to October 2027 and 2.2 years to October 2026 at 12%. Selected multiples are analyst judgments, not verified peer market multiples. No debt is subtracted a second time from P/E equity value.

**Subjectively weighted: ~$152/share at 12 months; ~$135/share present equivalent.** This mean is neither a median nor a confidence interval. Weights are analyst allocations conditional on utilization and continued access to funding; they are not measured likelihoods. A capital-access failure, counterparty failure or major contract dispute is not separately assigned probability. The full real-world outcome distribution can be worse than the slow case.

The 50% base weight reflects a rollout broadly consistent with the disclosed multi-site pipeline while limiting premium-price exposure. Slow receives 30% because acceptance timing, cost and funding can disappoint despite full usage after readiness. Bull receives 20% because it requires faster delivery, more high-price workload, additional capacity contracting and strong financing. These rationales do not statistically calibrate the numbers. At 20–26x base P/E instead of 24x, base 12-month value spans approximately $125–163. Probability-weighted value is particularly sensitive to the high bull outcome.

## Credit improves through cash earnings, not debt dollars alone

Base end-2028 debt is ~$78.1B versus modeled ~$30.1B EBITDA after SBC, or ~2.6x, excluding lease capitalization and rating-agency adjustments. Debt grows while the earnings base grows faster. Base 2028 interest remains ~$5.56B; improving percentage financing cost does not imply declining total interest while borrowing expands. Six-year D&A is ~$18.63B, income tax ~$1.18B and net income ~$4.74B on ~661M average economic shares. Operating margin after D&A/SBC is approximately 24.4%. Base still raises ~$3.48B equity in 2027 and ~$1.50B in 2028; operating success does not erase dilution.

No extra credit-driven multiple uplift is stacked on top: base 24x already assumes improved financing confidence. A hypothetical reduction of one rate point on $30B actually reset/refinanced adds $0.24B after 20% tax, about $0.36 per share at ~661M shares; fixed coupons do not automatically change.

## Equipment-life sensitivity

Changing **only new cohorts** to an eight-year accounting allocation, leaving legacy D&A at $9B, raises base 2028 modeled EPS to ~$10.03 and its mechanical 12-month P/E value to ~$210. This is not a forecast of a depreciation-policy change, prospective accounting on existing assets, or automatically justified equity appreciation. Book expense changes alone do not create cash. The six-year central model does not require this assumption.

## Backlog reconciliation and valuation revision

Base and bull revenues require post-June commitments and future bookings; the June RPO timing schedule remains intact. In particular, base revenue from H2 2026 through H1 2028 is roughly $58B versus ~$42.5B scheduled from June RPO; later business must bridge the difference. An old five-year contract cannot simply be consumed faster because more hardware comes online.

The earlier $103–121 12-month central range used $34B 2028 revenue and a top-down operating margin. This conditional model uses $47B, explicit capacity/premium-price mix, significantly higher depreciation and interest, and endogenous funding dilution. It produces about $150 central 12-month value. The revision is an assumption-driven scenario change, not a newly verified company guidance increase. Unsupported fleet-wide $40M/MW pricing is not used.

Validation: script executed; weights sum to one; quarter-by-quarter debt conservation verified; capacity monotonic and nonnegative; shares/cash nonnegative; revenue built from average capacity; totals and dilution recomputed. These checks validate arithmetic, not forecast accuracy or the chosen probabilities. No live price comparison or merge authorized.
