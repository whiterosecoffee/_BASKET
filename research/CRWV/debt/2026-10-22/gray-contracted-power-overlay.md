# CRWV: contracted power, backlog timing and Jon Gray overlay

October 22, 2026. USD. B10 #68 / draft PR #69. Continues capacity-conversion.md and capacity-weighted-valuation.md.

## Article retrieved

CNBC, October 22, 2026, “Blackstone's Jon Gray says CoreWeave can 'find a way through' financing pressure.” Exact full article retrieved through Firecrawl; the other search service's direct open failed. Article price widgets were not used as current quotes.
https://www.cnbc.com/2026/10/22/blackstone-jon-gray-coreweave-financing.html

Beyond the user-provided excerpt, Gray discussed higher compute pricing, better-than-expected value of older chips, and favorable incumbent data-center lease costs. He described the operating business positively while identifying capital access as the challenge. This is informed but commercially interested commentary from a major lender's leadership, not a disclosed new facility, waiver, full funding guarantee, company revenue forecast or changed customer recognition schedule. No full article reproduced.

Independent same-day Reuters reports Gray views wider credit spreads as an investment opportunity and identifies Blackstone as a significant CoreWeave lender. A lender can expect attractive returns on a new secured loan while common shareholders retain dilution/cost risk; lender confidence does not specify equity fair value.
https://www.reuters.com/legal/transactional/blackstones-profit-falls-choppy-market-tempers-investment-exits-2026-10-22/

An earlier **August 12** Blackstone-hosted CNBC transcript explains Gray's broader view that compute can become a financeable asset class because hardware retains value and is useful across customers. This is separate evidence, not part of the October interview. It supports using equipment collateral and contracted cash flow to broaden capital access, not assuming universal guarantees.
https://www.blackstone.com/news/in-the-news/cnbc-jon-gray-on-investing-in-the-ai-buildout/

## Why >4GW can be contracted before it is online

The ~4.2GW disclosed as of August 11 is **contracted input power/site capacity**. The ~$104.2B June backlog is **future customer service revenue**. They are opposite sides of the business and do not have a one-to-one or simultaneous recognition relationship. The public material does not establish that all contracted power is already fitted with GPUs, accepted, fully financed or tied to the June backlog. Equally, it is firmer infrastructure access than optional land/LOIs, and should not be dismissed as uncommitted speculation.

Sequence: execute future infrastructure contracts -> fund/build/fit out -> obtain service acceptance -> deliver recurring capacity over customer contract terms. Different sites enter these stages at different times. Indonesia's 360MW is in future contracted capacity but expected online in 2028. Helios phase-II halls start Q2 2027; phase III historically starts 2028. An activated MW can earn for several years; the same MW is not consumed once when a training job finishes.

At a hypothetical **fully billable 4.2GW**, annual revenue would be $42B at $10M/MW, $84B at $20M/MW, and $168B at $40M/MW. Those figures show the earnings potential of the footprint, but neither its delivery date nor its fleet-wide realized rate. The selected ~3–6-month $40M/MW contracts do not establish all 4.2GW earning that rate. Existing fixed customer commitments do not all reprice immediately.

Sources:
https://s205.q4cdn.com/133937190/files/doc_financials/2026/q2/CRWV-US-CORRECTED-TRANSCRIPT-CoreWeave-Q2-2026-Earnings-Call-11August2026.pdf
https://investors.coreweave.com/news/news-details/2026/CoreWeave-Continues-to-Contract-New-Compute-Capacity-at-Higher-Prices/default.aspx
https://www.coreweave.com/news/coreweave-expands-cloud-ai-platform-to-indonesia-marking-first-move-into-asia-pacific-region

## Reassessment of 'processing the backlog'

Three separate quantities:

1. **Contract value on deployments with service commenced:** June management disclosure >50% of backlog, targeting >two-thirds by end-2026. At $104.2B, two-thirds is ~$69.5B of contracts starting service, not the amount earned. A large share of the ~$100B book can therefore be operating before 2028. A date for all $100B commencing service is not verified.
2. **Revenue earned from the June book:** June 10-Q schedules 41% of $103.7B RPO (~$42.5B) by June 2028, 39% in the following two years, remainder through month 78. This remains the disclosed schedule. Gray does not amend customer service terms.
3. **Total cumulative company revenue, including later contracts:** can grow faster than recognition of the June book. The full-utilization scenarios imply approximately $59B / $80B / $110B over Q4 2026–Q4 2028 for slow/base/bull, using $4.622B illustrative Q4 2026 revenue. These are not percentages of the same old backlog. Bull could generate ~$100B total by late 2028; base would require additional 2029 revenue. Neither establishes earning the old $100B before January 2028.

Sources:
https://www.sec.gov/Archives/edgar/data/1769628/000176962826000366/crwv-20260630.htm
https://www.sec.gov/Archives/edgar/data/1769628/000176962826000104/crwv-20251231.htm

## Debt-definition reconciliation

June carrying balances, USD billions:
- Funded debt: **35.068**.
- Operating lease liabilities: **16.319**.
- Finance lease liabilities: **0.221**.
- Total: **51.608**.

This nearly exact reconciliation is consistent with CNBC's ~$51.6B broad debt figure being debt plus leases from the June balance sheet, not $51.6B of funded notes/bonds/loans. The article does not provide a complete October funded-debt reconciliation. Separate post-June financing and repayments still matter.

If rent already reduces EBITDA, charging funded-debt interest against the entire $51.6B additionally would mix lease and funded-debt costs. A lease-adjusted enterprise valuation can instead capitalize leases consistently with an EBITDAR denominator; do not mix those conventions. The earlier model's **$50B end-2026 funded debt** was an explicit conservative scenario assumption, not a reported balance, and this article does not validate it.

A separate **$45B end-2026 funded-debt sensitivity**, all other case assumptions unchanged and without pretending it is the verified balance, increases base 2028 modeled EPS from ~$7.17 to **$7.68**, and the 12-month equity value from ~$150 to **$161**. The model retains its simplified annual principal runoff, so this is not a newly reconstructed actual debt schedule.

## Valuation interpretation and new sensitivities

Gray's pricing and collateral arguments strengthen the operating thesis. They most directly challenge how quickly premium pricing normalizes and whether old equipment loses value at assumed rates. They do not independently establish more active MW today or faster original-contract recognition.

The existing base reduces new-cohort blended revenue/MW from $19M in 2027 to $17M in 2028. Holding that blended yield at **$19M in 2028** instead produces:
- 2028 revenue **$50.35B**, versus $47.05B.
- Economic EPS **~$9.82**, versus ~$7.17.
- 12-month capitalization at the same 24x and discount convention **~$206**, versus ~$150.

These figures are executed sensitivities in capacity-scenarios.py/json. Cash funding gaps and share issuance also change, so the EPS difference includes dilution effects. Neither alternative is added to the other without a combined run, and no separate collateral NAV or accounting-life uplift is stacked onto these earnings values.

Retain the existing **subjective conditional 30% slow / 50% base / 20% bull weights** rather than asserting a precise probability upgrade from supportive interview remarks. The ~$152 weighted 12-month result remains a scenario mean, not a statistically calibrated expected market price. Persistent premium economics support an alternative ~$200 case; a disclosed financing closing or verified delivery acceleration would be stronger evidence for moving scenario weights.

## Validation

Full CNBC page read; August Blackstone transcript kept separately dated; same-day Reuters cross-check; debt/lease sum recomputed; quarterly model rerun with all debt-conservation and nonnegative-state assertions passing. Previous primary RPO schedule preserved. No exact October capacity/debt update, blanket NVIDIA guarantee, new Blackstone financing, or full-backlog pre-2028 recognition is claimed. No merge authorized.
