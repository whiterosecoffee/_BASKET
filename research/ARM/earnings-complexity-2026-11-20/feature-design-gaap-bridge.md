# Forward GAAP EPS bridge

## Problem and relationship
Variant of feature-design.md under the same B12 research component. Separate 175x trailing GAAP valuation from forward adjusted EPS. Restore compensation and all other modeled exclusions while retaining ordinary development expense. Inputs are gaap-inputs.json; output is gaap-results.json, gaap-bridge.csv and GAAP_BRIDGE.md. Sources are separately dated and classified. Historical evidence is preserved.

## Formula and temporal boundary
Historical H1 inverse reconciliation, USD millions:
GAAP NI = 1046 - 720 - 138 - 12 - 7 + 108 + 123 = 400.
Q2: 566 - 377 - 48 - 12 - 20 + 21 = 130.
The gain and tax signs matter. H1 is fixed, including actual equity gains and discrete tax effects. Future gains are zero assumptions, not deletion of gains already recorded.

For FY27, adjusted annual NI = adjusted EPS anchor times assumed annual diluted shares. Forecast H2 adjusted NI is annual adjusted NI less filed H1 adjusted NI. H2 restored expense equals full-year modeled exclusions less actual H1 operating exclusions. H2 GAAP NI equals H2 adjusted NI less H2 restored costs and extra development, multiplied by one minus the marginal tax shield. Add actual H1 GAAP NI and divide by annual diluted shares. Do NOT tax or adjust H1 a second time.

For FY28, GAAP NI = adjusted EPS anchor times shares minus (restored compensation + employer taxes + acquisition + other exclusions + extra development) times (1 - marginal tax shield). Divide by shares. Future equity gains are zero. All spending already embedded in adjusted EPS remains in the baseline. extra_development means a miss relative to that budget, not all chip-development expense. Normal depreciation remains expensed; capex is not additionally expensed wholesale.

## Scenario design
Flat Q2 costs annualizes P&L compensation including software SBC amortization, employer taxes and acquisition adjustments. Higher compensation assumes SBC of $1.85B in FY27 and $2.40B in FY28, plus separately declared employer taxes/acquisition costs. This is a transparent sensitivity motivated by $3.4066B of unrecognized awards over a weighted-average 1.5 years. Division by 1.5 is NOT used to fabricate a vesting schedule or minimum annual expense. The overrun variant adds $100M in FY27 H2 and $300M in FY28 above the embedded development budget.

Assumed shares 1.090B and 1.110B reflect future dilution separately from compensation expense. Keep modeled NI fixed for share-count sensitivity. Tax shield is 15% in the reference scenario with 0% and 25% alternatives, not a guarantee that tax benefits are realized. Arm has no future GAAP guidance bridge. There are no scenario probabilities.

## Operating-budget sanity check
Given total revenue, illustrative hardware revenue and gross margin, IP margin before restored costs, net interest, adjusted tax and shares, solve for operating expense budget consistent with adjusted EPS. This budget INCLUDES R&D. Test the budget against 15% growth; do not assert it is the actual analyst cost model. At fixed total revenue, increasing hardware mix reduces gross margin relative to licensing IP. An additional hardware dollar still provides positive gross profit. Shared R&D cannot be allocated precisely between IP and silicon from the filings.

## Prior art, evidence and exceptions
Use the issuer's H1/Q2 reconciliation instead of extrapolating a trailing EPS gap. Q2 376m is the cash-flow SBC line; 377m includes software amortization and is the correct P&L restoration. Fiscal 2028 ends March 2028. Consensus inputs are Nov17 vintage. Third-party GAAP net-income forecasts provide a separate cross-check, not a matched analyst panel.

## Review and falsifiers
Reconcile both historical periods exactly; retain H1 equity gains; verify scenario cost totals, ordinary R&D retention, monotonic cost sensitivity, tax and share sensitivity, deterministic replay and owned paths. Higher future excluded expenses reduce GAAP EPS. Faster royalty revenue, better gross margins, lower compensation recognition or tax credits can improve results. A strong technical position does not establish any fair-value P/E. Independent review remains required.
