# SFTBY capital conversion — research prototype
Date: 2026-11-20. Spark B09. Issue #300. Branch work/300-sftby-capital-conversion-rotation.

## Scope
Quarterly scenario workbook (2026 Q4–2030 Q4), delivered as local user attachment SFTBY_capital_conversion_2027_2030.xlsx. The workbook is not committed as a binary repo artifact. This Markdown records its assumptions, limitations, and reproduction contract. Not a production engine or verified current NAV.

## Model separation
- Arm: Q2 FY27 licensing USD 773M, royalty USD 670M, total quarterly sales USD 1.443B (https://newsroom.arm.com/news/arm-q2-fye27-results). Model hypothetical licensing/royalty growth, direct silicon sales and profitability separately. ARM shares are valued using a scenario market-price path. Do not add earnings atop NAV a second time.
- OpenAI: scenario annualized revenue USD 50B, starting gross valuation USD 1.25T, gross ownership 13%, scenario parent NAV capture 65%. Private-company valuation, actual revenue definitions and net fund waterfall are unverified. Apply *incremental* changes relative to starting embedded mark, never add entire stake again to SVF2.
- SB Energy: November 18 SEC S-1/A says 8.8 GW IT contracted/in development but 0 GW IT operating; revenue cannot begin until ready-for-service and tenant acceptance. USD 439B is issuer-estimated backlog, not recognized revenue. Source https://www.sec.gov/Archives/edgar/data/2133037/000162828026075026/sbenergy-sx1a3.htm. Revenue/accepted GW and project cashflow are illustrative and NOT consolidated into parent NAV or liquidity absent actual ownership and distribution terms.
- Parent: scenario start NAV USD 251B (mechanical research mark), adjusted debt USD 72B, post-October hypothetical liquidity USD 21.6B (NOT verified unrestricted cash). Parent cash changes via asset rotation, new debt, repayment, new committed capital, assumed recurring cash and financing drag. Mark-to-market is not free cash flow.
- Model key output: incremental NAV alpha from *newly invested* dollars after parent financing/overhead drag, divided by cumulative new parent investment. Under a scenario, total NAV can rise even if incremental investment alpha is negative.
- Quarterly group LTV proxy = adjusted debt/(NAV+adjusted debt). It is not an ARM loan covenant or verified current group LTV.
- Stated historical normal discount hypothesis 50%; actual scenario endings adjustable in workbook. No numeric probabilities.

## Three scenarios at 2030 Q4 from formula workbook
Base: NAV USD 384.3B; ADR USD 13.49; group LTV 13.5%; parent cash USD 25.1B; net new-capital alpha/invested -30.7%.
Credit stress: NAV USD 119.8B; ADR USD 4.20; group LTV 45.7% (violates SoftBank extraordinary ceiling without management intervention); parent cash USD 12.6B; net new-capital alpha/invested -72.0%.
Active rotation: NAV USD 373.2B; ADR USD 14.73; group LTV 8.5%; parent cash USD 34.6B; net new-capital alpha/invested -17.7%.
All are scenarios, not issuer forecasts. The stress result is not a realistic maintained financing trajectory because action would likely be required earlier.

## Falsifiers and next gate
Requires reconciliation of: dated and unrestricted parent cash; exact ARM collateral triggers and pledged/unpledged units; OpenAI parent-attributable economics embedded within SVF2; SB Energy ownership/project debt; revenue/FCF definitions; and actual rotation proceeds and disposal costs. B09 #28 owns look-through interface; B04 #30 economic valuation. Re-run source checks and scenario tests before using this as a current SFTBY NAV or investment decision.
