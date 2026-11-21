# CRWV funding and earnings hurdles — November20,2026

At the frozen $39.51 regular close, value depends on converting delivery into GAAP earnings while meeting project and parent cash obligations. The $9B expected deposits do not yet provide verified receipt evidence. The financing thesis is conditional; no source supports a completed monthly funding proof.

## Reuse and source coverage

Reused PR289 at fc4fc696674acf3f7f64842a18c770c217754a40 after opening its AGENTS/state/README/HANDOFF/result. It already supplies the historical audit. Owner86/PR87 keeps the finance engine. This research adds no code/model/ingestion. Current121branch scope is unchanged; prior reports remain historical.

The SEC submissions provider returned the Nov12 10-Q and Nov10 earnings8-K for Nov1–20 under forms10-Q/8-K/424B5. No subsequent financing-close/deposit receipt confirmation appeared in that bounded inventory. That does not prove no private receipts. Massive's filing endpoint returned an empty set despite the known filing; the SEC provider supplied the replacement evidence. Massive daily summary independently reconfirmed $39.51 close and $40.9453 AH summary; the latter has no exact trade timestamp in this endpoint. Sessions have ended.

## Funding facts that constrain the bridge

At September30, consolidated cash/securities were $4.184B; $5.653B facility availability gives reported $9.837B liquidity. The availability is undrawn and conditional. $2.282B restricted cash is separate. None of these aggregates establishes freely distributable parent cash or today's balances.

The filing reclassified approximately $1.9B from deferred revenue to customer liabilities because contracts became cancellable; the customer liability balance was $1.915B. This is not evidence of customer cancellations, refunds paid or a default. Obtain contractual refund triggers and timing before treating those deposits as durable financing. Do not mechanically subtract the full liability from cash.

DDTL5.5 already existed before the November call: August agreement/closing announcement; $2.6B commitment and $1.555B September carrying balance, which is not drawn principal. Its draw window ends December31 and monthly installments begin February2027. After draw-window termination, excess monthly cash must prepay loans until principal reaches $1.3B. This cash sweep means project performance need not immediately become parent/shareholder cash. The future DDTL discussed November10 is a different, still unconfirmed transaction in this source check.

DDTL5.0 availability ended September30 and amortization begins November2026. DDTL4.0 remains subject to eligible-asset/DSCR/project conditions, reserve requirements and site/draw-dependent principal triggers; it is nonrecourse with limited carveouts. Other DDTLs include parent guarantees. Expected final installments and legal/table maturities are kept separate. Neither headline maturity nor total committed GW supplies monthly debt service.

Management's $9B future receipts include over$3B tied to existing infrastructure; do not add the subset twice. Nearly$5B available DDTL and September's availability need a date bridge, not addition. More than$9B construction in progress is equipment/cost already on the balance sheet, not fresh cash. Actual post-statement receipts and next-facility draws remain null.

## Earnings and period discipline

Q3 CFO $1.975B minus cash PPE $9.441B gives −$7.466B; nine-month figures are separately $5.638B and $23.558B, giving −$17.920B. These are mechanical cash measures, not economic returns on the deployed fleet. Do not mix the two periods or reported total-capex definitions. Q3's $2.127B deferred-revenue cashflow adjustment is not gross deposits received and cannot be added again to CFO.

Implied Q4 adjusted OI is $747–847M versus interest guidance $1.05–1.15B: a $203–403M shortfall before other nonoperating/tax effects. Improving operations therefore does not alone establish net profitability. Principal payments stay outside EPS but inside funding.

## What $39.51 requires from FY2028 earnings

Isolated sensitivity: $44.36B revenue (unreconciled third-party estimate),25% tax on positive income,556.126M shares held flat, zero other pretax income/expense. These are assumptions, not a sourced2028 forecast. GAAP operating margin retains depreciation and SBC. The interest cases are explicit sensitivities; $4.4B is merely annualized midpoint Q4 guidance, not promised2028 cost.

| Annual expensed net interest | Pretax breakeven GAAP margin | Margin for25× FY2028 EPS | Margin for20× FY2028 EPS |
|---|---:|---:|---:|
| $4.4B | 9.9% | 12.6% | 13.2% |
| $5.5B | 12.4% | 15.0% | 15.7% |
| $7.5B | 16.9% | 19.5% | 20.2% |

At this price/flat denominator,25× needs ~$879M GAAP net income and20× needs ~$1.099B. Every extra $1B annual expensed interest reduces EPS about$1.35 at the assumed tax/shares; one percentage point of GAAP operating margin adds ~$0.60 EPS. Future dilution makes the hurdle higher. A full hypothetical35M-share ATM at$39.51 raises ~$1.383B gross and reduces EPS~5.9% if earnings stay unchanged; authorization is not actual issuance. This is not a discounted target price or funded cash-flow valuation.

The bull case needs accepted/billable conversion, receipts, cheap eligible draws and retained earnings after project sweeps. The failure case is late acceptance or weaker funding terms forcing delayed deployments, refunds or dilutive parent capital. Neither probability is calibrated. Demand alone cannot distinguish them.

## Validation and next action

JSON/markdown inputs and six reverse-multiple cases were checked with independent Python arithmetic; period cashflow/liquidity identities and null funding/receipt gates passed. No finance engine code changed. PR289 tests were not rerun here and its independent new-domain CI remains separate.

Next: owner86 should map actual deposit receipts/refund terms and DDTL5.5 excess-cash sweep/eligible draws into monthly project-to-parent liquidity. Keep the funding gap and definitive forward GAAP P/E unknown until source closure.

Sources: [Q3 10-Q](https://www.sec.gov/Archives/edgar/data/1769628/000176962826000465/crwv-20260930.htm), [results](https://www.sec.gov/Archives/edgar/data/1769628/000176962826000461/coreweave3q26earningspress.htm), [call transcript](https://s205.q4cdn.com/133937190/files/content_files/CoreWeave-3Q26-Transcript-_1_.pdf). Exact periods, source times, source-query coverage and formulas are in the paired JSON.
