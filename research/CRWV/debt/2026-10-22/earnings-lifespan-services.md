# CRWV: operating earnings, equipment life and services

October 22, 2026. USD. B10 / issue #68 / draft PR #69. Historical trailing window ends June 30, 2026; no October earnings run rate is asserted.

## Trailing earnings bridge

Use FY2025 minus H1 2025 plus H1 2026. Figures below are USD millions. Rounded financial statements limit precision.

| Measure | FY2025 | H1 2025 | H1 2026 | Trailing June 2026 |
|---|---:|---:|---:|---:|
| Net loss | -1,167 | -605 | -1,366 | -1,928 |
| D&A, cash-flow statement | 2,454 | 1,003 | 2,540 | 3,991 |
| Net loss plus D&A | | | | 2,063 |
| Interest expense, net | 1,229 | 531 | 1,176 | 1,874 |
| Adjusted EBITDA | 3,093 | 1,360 | 2,667 | 4,400 |

At a consistent **551M shares**, the Q2 2026 basic weighted-average count, trailing net loss is **-$3.50/share**, while net loss plus D&A is **+$3.74/share**. These are normalized per-share calculations, not reported trailing GAAP EPS, a fully diluted positive-earnings calculation, or a current share count. They retain booked interest, stock compensation and the reported tax provision. D&A is added back without hypothetical tax normalization. Other noncash income/expenses remain, so the result is not actual operating cash flow.

For comparison, approximate period-weighted basic shares are 521M: derive H2 2025 at about 503M from FY435M and H1 367M, then average with H1 2026's 539M. That produces about **-$3.70/share** loss and **+$3.96/share before D&A**. This uses rounded half-year weighting, not the exact daily denominator. Preferred dividends in FY2025 and H1 2025 cancel in this trailing common-income bridge. Positive adjusted earnings would require reassessing dilution; the historical anti-dilutive count is not automatically appropriate.

**Growth capex already sits outside the income statement.** It cannot simply be added back to EPS. Construction in progress is not depreciated before intended use. Certain construction-period interest is already capitalized rather than expensed. Neither all D&A nor all interest can be labeled expansion-only: operating equipment wears out and operating fleet debt costs money.

The +$3.74 figure therefore measures earnings before the accounting allocation of equipment/intangible cost; it does not establish sustainable distributable earnings. Replace D&A with an explicit economic equipment-renewal reserve to explore that distinction. At 551M shares, an illustrative $1B annual reserve lowers it to **$1.93/share**; a $2B reserve lowers it to **$0.11/share**. Reserve assumptions are not company guidance or an estimate of actual maintenance capex. These sensitivities retain reported tax provision and other items unchanged; they are not complete tax-normalized owner-earnings models. Principal repayment, working capital and mandatory reserves further affect cash distributable to equity without being EPS expenses. A mature-fleet result also needs a defensible allocation of startup/ramp costs and growth financing, which the consolidated disclosure does not supply.

Sources:
- https://investors.coreweave.com/news/news-details/2026/CoreWeave-Reports-Strong-Fourth-Quarter-and-Fiscal-Year-2025-Results/
- https://investors.coreweave.com/news/news-details/2026/CoreWeave-Reports-Strong-Second-Quarter-2026-Results/
- https://www.sec.gov/Archives/edgar/data/1769628/000176962826000104/crwv-20251231.htm

## Equipment life: EPS, asset value and equity value

CoreWeave uses six-year technology-equipment depreciation. Physical function, profitable operating life and accounting life are different. Older GPU renewals support an economic tail but architecture launch date does not establish the age of individual purchased units. The existing integrated assessment records the A100 contract into 2029 and a three-year H200 renewal. Remaining maintenance cost, power opportunity cost, software compatibility, customer pricing and utilization determine the tail's value.

For a new $10B eligible equipment cohort, zero residual, straight-line depreciation, an assumed 20% effective tax rate and 600M modeled shares:

| Assumed life | Annual D&A | Annual EPS improvement versus six years |
|---|---:|---:|
| 6 years | $1.667B | — |
| 7 years | $1.429B | $0.32 |
| 8 years | $1.250B | $0.56 |
| 9 years | $1.111B | $0.74 |

This is a fresh-cohort sensitivity, not a forecast of a disclosed accounting change. For existing assets a revised life applies prospectively to remaining book value and remaining life. For example, $10B original cost at age two has $6.667B remaining under a six-year schedule; extending total life to eight means six remaining years and $1.111B annual D&A, compared with $1.667B previously. There is no immediate write-up reversing past depreciation.

Less depreciation raises subsequent reported earnings/book equity, with tax effects depending on accounting. It does not directly raise EBITDA or cash flow. Tax depreciation is separate. Economic NAV rises if equipment earns additional net cash, needs less replacement investment, or realizes a better sale value. Avoid adding the same tail cash flow once in NAV and again as capitalized EPS uplift.

An illustrative additional $1B/year cash flow at year-ends seven and eight is worth about **$0.856B today at 12%**, before any additional claims not already deducted from that cash. At 600M modeled shares that is about **$1.43/share**. This is a valuation sensitivity, not a price target. The screenshot's $31.28B capitalization and $56.71 price lack a quote date; neither independently identifies the market's assumed GPU life. Funding, dilution, discount rates and first-contract returns can reproduce the same stock price under different useful-life assumptions.

## Services: an existing route to greater value per customer

CoreWeave already offers the kind of applied solutions work in the question. Physical AI Field Engineering, launched September 10, 2026, embeds engineering specialists to build and deploy models on customer data, drawing on Monolith AI. This can generate services work and demand for compute. Consulting labor can lower percentage margins even while lifting total profit; the scalable opportunity is repeatable software and recurring workloads enabled by those engagements.

Forge, announced September 30, integrates Weights & Biases with managed development, evaluation, inference and agent execution tools. W&B's cross-cloud position can support software monetization without owning every underlying GPU. Adoption figures are not a disclosed paying-customer count, services revenue or proven segment margin. Launchables productizes deployment recipes, but third-party tools in a template do not automatically create a proprietary software license stream.

Analyst assessment: recurring workflow software, managed inference and reusable industry applications offer greater operating leverage than a large bespoke consulting workforce. They can increase customer retention, storage/compute consumption, and potentially profit per MW. Better inference efficiency benefits CoreWeave directly when charging for output or selling more workload; with fixed reserved-capacity pricing, efficiency may first benefit the customer unless CoreWeave captures it through pricing or additional consumption. Matching smaller models and industrial workloads to older GPUs can extend profitable use, subject to power economics. Separate services revenue, attach rates and incremental margins are needed before assigning a software-like valuation to the entire company.

Sources:
- https://www.coreweave.com/news/coreweave-launches-physical-ai-field-engineering-to-turn-proprietary-data-into-production-ai
- https://www.coreweave.com/blog/coreweave-forge-turn-ai-iteration-into-compounding-improvement
- https://www.coreweave.com/companies/weights-and-biases
- https://www.coreweave.com/blog/introducing-coreweave-physical-ai-launchables-run-workloads-with-one-command

## DGX Spark and replacement-cost signals

NVIDIA's official February announcement raised Founders Edition MSRP from $3,999 to $4,699 without changing configuration, citing memory constraints. Subsequent reporting describes 128GB retail offerings around $7,000–$9,000 and a different new 64GB configuration at $4,999. An identical-config $4,999-to-$8,000 change was not independently established here. Spark's memory/configuration is not a direct price index for CoreWeave's HBM-equipped data-center fleet.

Higher replacement cost can favor an installed operator if customer pricing responds and procurement is protected. It does not write up historical-cost PP&E or establish a like-for-like rise in the economic value of every installed GPU. Compare complete delivered infrastructure cost, contract pricing and remaining earning life.

Sources:
- https://forums.developer.nvidia.com/t/2-23-2026-price-change-announcement/361713
- https://www.tomshardware.com/pc-components/gpus/nvidia-introduces-64gb-dgx-spark-to-throw-local-ai-fans-a-lifeline-amid-the-rampocalypse-new-gb10-config-starts-at-usd4999-for-those-who-can-work-with-less

Validation: arithmetic recomputed from rounded published statements; all per-share denominators and hypothetical assumptions labeled. No exact maintenance-capex estimate, mature-fleet EPS, implied market useful life or present-day debt/share balance is claimed.
