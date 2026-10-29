# CRWV — evidence-granularity and peer valuation assessment (2026-10-29)

Issue #113 | Spark B10 | as-of 2026-10-29 | Scope: research-only. Not a live quote or calibrated price forecast.

## Verdict
The investment hinge is *conversion of contracted power into funded, energized, billable clusters and durable cash flow to common equity*, not backlog or adjusted EBITDA alone. A naive EV/revenue multiple understates financing seniority, GPU replacement and dilution. No defensible single price target is issued without instrument-level monthly funding and shareholder claim reconciliation.

## Verified dated baseline
- Q2 2026 revenue $2.575B (+112% YoY), adjusted EBITDA $1.510B, GAAP net loss $626M, net interest expense $640M; Q2 revenue backlog $104B *excluding* >$25B new commitments early Q3. Source https://investors.coreweave.com/news/news-details/2026/CoreWeave-Reports-Strong-Second-Quarter-2026-Results/ (published 2026-08-11, Q2 period end 2026-06-30).
- Contracted power 3.7 GW and active power 1.5 GW at June 30; contracted increased to ~4.2 GW as of Aug 11, reiterated October 27. Do not add 1.5GW active to 4.2GW contracted. Sources https://investors.coreweave.com/news/news-details/2026/CoreWeave-Continues-to-Contract-New-Compute-Capacity-at-Higher-Prices/default.aspx and https://investors.coreweave.com/news/news-details/2026/CoreWeave-Expands-Global-AI-Cloud-Platform-With-New-Capacity-in-Denmark-and-First-Global-AI-Network-Backbone/default.aspx
- Short-duration three-to-six-month Q3 contracts reported at ~$40M/MW of annualized revenue. NOT portfolio-wide realized pricing; separate price cohorts. Source Sept 17 company press release above.
- $35.6B debt at June 30 and ~$10B undrawn capacity in named facilities; undrawn != outstanding debt. Source https://www.sec.gov/Archives/edgar/data/1769628/000176962826000366/crwv-20260630.htm
- DDTL 4.0 $8.5B facility floating at SOFR+2.25%, due March 2032; DDTL 5.5 $2.6B facility at SOFR+5.50%, due September 2031. Facility size != amount drawn. Sources https://www.sec.gov/Archives/edgar/data/1769628/000176962826000129/crwv-20260330.htm and https://www.sec.gov/Archives/edgar/data/1769628/000176962826000357/crwv-20260807.htm
- Oct 27 company reported majority of 22.5MW IT capacity online at Copenhagen DEN01. It is a site-level update, not independent incremental proof of total portfolio power.
- Third-quarter earnings scheduled November 10, 2026, 5 p.m. ET: https://investors.coreweave.com/news/news-details/2026/CoreWeave-Announces-Date-of-Third-Quarter-2026-Financial-Results-and-Conference-Call/default.aspx

## Required per-resource/cohort profiles
1. Site identity, power definition (gross vs IT MW), exclusivity, lease/contract/options/LOI, customer and geography.
2. Utility interconnection, energization, commissioning, active and billable MW separately; effective dates and capacity constraints.
3. GPU type, delivery, capitalized cost, lifespan, depreciation, replacement/upgrade and residual value; purchased vs financed ownership.
4. Customer contract: signed status, start/end, service acceptance, reservation, take-or-pay, actual tariff, ramp, pricing vintages, cancellation and credit counterparty.
5. Per-instrument debt: committed/drawn/undrawn, interest benchmark/spread/fixed component, collateral, contract linkage, fees, maturity, amortization, covenant and refinancing state.
6. Equity waterfall: GAAP operating earnings, interest, taxes, maintenance vs expansion capex, net funding gap, future issue/convert dilution, fully diluted shares and per-share cash generation.
7. Append-only sourced records with observed/available/ingested/effective times; reconcile site-level rollups and parent/subsidiary double counting.

## Comparative investment standing
- CRWV: stronger presently recognized AI cloud revenue scale; high funded-asset deployment and leverage risk.
- NBIS: rapid deployment, different cash/prepayment and customer financing mix; avoid saying 'less risky' without audited matched dates and capital structures. Q2 shareholder letter https://www.sec.gov/Archives/edgar/data/1513845/000110465926094568/tm2622968d1_ex99-2.htm
- IREN: data center/AI-cloud hybrid; distinguish contracted ARR from earned AI cloud revenue, project power from billable GPU power, funding/ownership.
- Compare each on net incremental equity cash yield per *new billable MW*, power-to-billing lag, ROIC minus cost of capital, secured debt per billable MW, dilution, counterparty concentration, 24-month funding gap, and renewal/replacement economics. Overall equity ranking **not established** until reconciled matched-date peer models exist.

## Prior-art families to incorporate
- Project finance and infrastructure waterfall: instrument-by-instrument collateral and seniority, draw conditions, debt service coverage, maturity/refinancing and equity residual.
- Utility/grid development: interconnection queue, contracted vs energized capacity, gross-to-IT conversion and construction critical path.
- Telecom/data-center unit economics: cohorts/vintages, reserved vs billable utilization, effective yield/MW, depreciation and renewal lifetime.
- SaaS/RPO and credit underwriting: bookings/backlog vs recognized revenue; performance conditions, concentration and counterparty credit.
- Semiconductor fleet lifecycle: hardware aging, useful-life sensitivities, GPU upgrades/trade-in, economic vs accounting depreciation.
- Real options/staged investment: exercised capacity vs expansion options and LOIs, capex required before option value realizes.
- Equity valuation: FCFE/DCF, enterprise-to-equity bridge, scenario sensitivity, reverse-implied growth, dilution and multiple compression.
- Point-in-time research/data lineage: immutable evidence and vintage dates, contradiction/overlap graph, independent counterparty cross-check.

## Reusable decision gates
Q3 actuals and 2027 guidance; roll-forward Aug 4.2 GW into site-level energized/billable cohorts; reconcile undrawn vs outstanding facilities, rate exposure and future secured claims; customer acceptance/ramp dates; funding needs through 2028; fully diluted share bridge. If missing, show 'not established', never fabricate precision.

## Prior repo art and ownership
Read/extend rather than duplicate: #68/PR #69 debt and prior-art review; #86/PR #87 offline monthly waterfall and scenario engine; #95/PR #99 traversal; #100/PR #101 market context; #112 repository-first persistence. B04 owns generic shared valuation methods; B02 price data; B01 independent CI. This note is only ticker research and makes no claim those draft PRs are merged or deployed.

Source status: primary issuer/SEC where stated, third-party methodological comparison only; provider publish/ingest time for this GitHub note is commit time, not invented earlier timestamps.
