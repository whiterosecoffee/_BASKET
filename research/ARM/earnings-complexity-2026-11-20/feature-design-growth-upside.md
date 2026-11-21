# ARM growth transmission and long-horizon upside

## Contract and relationship
Parent: feature-design-gaap-bridge.md and AGENTS.md. This research variant addresses the growth mechanism that near-term GAAP scenarios do not fully describe. Inputs: growth-upside-inputs.json; replay: python growth-upside.py; output: growth-upside-results.json. The existing GAAP expense scenarios remain unchanged and address a different horizon.

## What is growing
For September 2026, total revenue grew 27%, licensing 50%, total royalties 8%; management described data-center royalties as doubling, physical AI as +50%, and edge as roughly flat. New design commitments and current production revenue are different cohorts. Thus the total royalty figure alone cannot describe custom-server design momentum. Source: November call and results in the input manifest.

The reusable operating relationship is royalty revenue = sum over shipped product cohorts of units times contractual royalty per chip. More cores and richer IP can raise dollars per chip; their economic effect depends on contract terms and when those designs ship. An illustrative 20% increase in units and 20% increase in royalty content yields 44% growth for that cohort, not automatically for the full company. Do not add this growth to an already comprehensive royalty forecast a second time.

## Why complexity and units do not immediately produce company-wide acceleration
1. Design access, engineering and tape-out precede high-volume shipments. Licensing growth can appear before the associated royalty ramp. Arm nevertheless accrues royalties in the customer's shipment quarter using estimates, with subsequent true-ups. A reporting delay is not a blanket extra quarter of deferred GAAP royalties.
2. More chip complexity only increases Arm revenue insofar as the contract captures it. Agreements can specify fixed fees or percentages of chip ASP; some have declining royalty tiers as cumulative volume rises. The filing also classifies certain royalty buy-downs and upfront minimum commitments in licensing revenue. These terms can affect timing/mix; the exact impact on this quarter is not quantified.
3. Phone-memory cost pressure offsets richer Armv9/CSS content in the existing edge base. This is a management explanation; we do not have quarter-matched segment royalty dollars to prove the complete 8% weighted bridge. Do not use an annual segment mix as the current-quarter weighting.
4. The new direct-chip business has not yet reached commercial volume: planned first shipments are FY27 Q4. Supply availability and acceptance gate that revenue.

## The long-term model omitted from the earlier near-term discussion
Arm's investor-session model targets FYE31 revenue of $25B: $10B IP plus $15B AGI CPU, with more than $9 adjusted EPS. It assumes about 20% annual core-count growth and mid-teens adjusted opex growth. It is a public management target, not evidence of an analyst omission. Relative to the FY28 anchors of $8.37B revenue and $3.09 adjusted EPS, the $25B/$9 reference requires roughly 44%/43% annual growth over three years. Robotics is largely a post-FYE31 opportunity in that model and remains unquantified here.

## Gross profit matters as well as margin
Arm's illustrative chip example shows how selling a full processor can generate more gross-profit dollars despite a lower percentage margin. That helps explain why direct silicon could materially change EPS. Later earnings commentary puts first-generation chip gross margin around 30-40%; the long-term model requires at least 50%. Those are different stages, not interchangeable assumptions. Ordinary development spending, compensation, manufacturing risk and customer overlap must still be retained.

## Unknown versus unpriced
Known drivers: core count, CSS/richer IP, custom-server deployments, agentic CPU demand and direct-chip expansion. Potential further upside: faster adoption, richer realized pricing, earlier robotics and future accelerator products. No matched analyst model proves these are omitted from consensus. No incremental EPS is assigned to an undisclosed accelerator program. Contracted royalty rates are not guaranteed volumes or take-or-pay backlog.

## Valuation method and limitations
The arithmetic uses a $9 adjusted EPS reference rather than treating a greater-than target as an exact forecast. At the historical $152.20 close this is about 16.9x distant earnings, around 4.36 years away. An illustrative 30x multiple on $9 produces $270 at March 2031; discounting that future price is a horizon sensitivity, not an intrinsic-value DCF. Compensation, share-count and GAAP EPS for FY31 are unresolved. No scenario probabilities or fair-value conclusion are asserted.

## Review and next action
Replay checks date horizon, growth rates, cohort arithmetic and scenario count; preserve exact input hash. Source names and URLs are in growth-upside-inputs.json. Earlier near-term premium conclusions should not be presented as a complete long-horizon valuation. Next: build a dated royalty cohort bridge using quarter-matched shipped units, dollars per chip and absolute segment revenue; until available, report the missing fields explicitly.
