# Evidence-to-company analysis contract

Version: company-analysis-method/0.1.0-draft. Parent: repository guidance. First instance: ../orcl_analysis/state.json.

## Problem and boundaries
A ticker can look inexpensive because future EPS is overstated, accounting exclusions are large, future dilution is missing, cash is consumed by growth, or the business mix justifies a lower multiple. A defensible analysis must expose these differences before turning a growth story into a share-price path. This method organizes source-backed research and delegates domain computation; it is not an automated predictor or live market service.

## Contract and classifications
Inputs carry source_id, URL/source class, publication date, effective_at, period_end, observed_at, available_at, ingested_at, model version and validity. Unknown intraday publication times are null, not invented midnight timestamps. Record observed values, issuer statements/targets, counterpart statements, third-party consensus, analyst hypotheses, modeled scenarios and unknown/conflicted evidence separately. A verified document can contain an unverified future forecast.

Output sections: identity/as-of; investment question; revenue/profit map; management and governance; partnership monetization/status map; internal technology vs purchased components; moat/erosion; bottom-up addressable spending; EPS/calendar/GAAP bridge; financing/cash; same-horizon valuation and discount channels; competing hypotheses; priority watchpoints; source/correction ledger; implementation/review state.

Each partnership row has counterparty, role, announced/signed/available/deployed/billed/recognized status, monetization path, margin/capital effect, concentration, source and next proof. Each opportunity identifies buyer, budget, procurement/qualification, serviceable capacity, price, margin, working capital and reinvestment; overlapping spend is not additive. A TAM total without those components remains unknown.

## Procedure
1. Reconcile current repository branch/ownership, existing components and previous corrections. Record planned child capabilities before expanding scope.
2. Verify identity, fiscal periods, release dates and source vintage. Request existing FETCH refresh before any market-data read. Retain prior reference prices as historical, not executable quotes.
3. Map revenue once by reported line, then tag products/themes as overlays. Do not add nested SaaS/database/AI exposures twice.
4. Trace paid customer value, production deployment, renewals and partner economics; list unpriced/bundled product features separately.
5. Reconcile income statements, taxes, diluted shares and preferred rights. Bridge adjusted-to-GAAP with explicit excluded items. Annualize a quarter only as sensitivity, never as consensus.
6. Schedule construction/acceptance/billing, leases, cash/vendor financing, depreciation and replacement. Separate contract signing, accepted capacity, cash collection, accounting revenue and profit.
7. Build a dated EPS ladder with origin labels and range. Compute growth and constant-price multiples. Use matched-period peer evidence if available; otherwise show illustrative multiples, not an invented discount or fair value.
8. Stress correlated failures, downside and cost of waiting; retain disconfirming evidence. Fundamental scenarios do not establish trading probabilities or traversal bands.
9. Apply review.md; update contextual state and append dated evidence/corrections. Publish on owner branch and verify remote bytes/head. An issue comment alone is not file integration.

## Equations
YoY EPS growth = EPS_t / EPS_(t-1) - 1. Cumulative EPS growth = EPS_t / explicit baseline EPS - 1; do not sum annual percentages. Nonpositive baselines require sign-aware absolute comparison, not misleading growth ratios.

Fiscal-year P/E = reference price / that fiscal-year EPS. NTM requires an independently constructed rolling next-twelve-month denominator. Same-P/E price equivalent = reference_price * EPS_t / reference_EPS. This is a conditional price equivalent, not the date a market must reach it. Total returns require dividends, taxes, transaction costs and account constraints separately.

Common EPS = (pretax earnings - tax - applicable preferred distributions - other common-claim adjustments) / weighted diluted common shares. If-converted treatment adjusts numerator and denominator consistently. Financing cash is not operating profit; cash interest and accounting interest differ when capitalization/accruals apply.

Reported FCF = reported CFO - reported cash capex under the disclosed definition. Owner-cash view must separately reconcile SBC/dilution, vendor/finance-lease principal, working capital/prepayments, maintenance/replacement and growth investment. No arbitrary exclusion of growth capex and no second deduction of lease costs already expensed.

Revenue-delay sensitivity = delayed revenue * (1 - avoidable cost fraction). This assumes fixed obligations persist and variable spend can be avoided; a margin shock is an alternative specification, not an extra deduction for the same effect.

## Discount method
Assign each risk to forecast amount/timing, reinvestment/capital needs, dilution/claims, discount rate or justified terminal multiple. Do not apply the same risk to every axis. A weak cash bridge can justify a lower multiple, but no numeric haircut is established without comparative or calibrated evidence. Rate relief reprices floating/refinanced/new obligations; fixed coupons do not instantly change. Model duration and refinancing years explicitly.

## Prior-art families and promotion
Driver-based financial planning and cohort/project finance inform capacity-to-cash; accounting quality and sum-of-parts inform business mix; reverse valuation and scenario analysis expose implied expectations; event-sourced evidence and point-in-time research prevent lookahead; hypothesis/falsifier registers prevent narrative lock-in; domain-driven design and ports/adapters keep fetch/model/presentation separate. These are organizing influences, not claims of implementing a specific vendor framework. Promotion requires a second ticker, retained exceptions, accounting/date failure cases and independent review. Prefer composition over a universal score or duplicated monolith.

## Limitations
No validated probabilities, investment recommendation, current executable ratio, benchmark regression, independent source audit, legal contract opinion, persistent worker or automatic file inheritance is implied. Exact source documents/hashes, entitlements and downstream acceptance remain separate gates.
