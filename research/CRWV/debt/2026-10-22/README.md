# CRWV debt stack and contract-financing audit
As of October 22, 2026. USD throughout. Research version 1.0.0; B10 issue [#68](https://github.com/whiterosecoffee/_BASKET/issues/68).

**Assessment:** Management does match most infrastructure financing to customer cash flows, and several recent financing terms were materially better than the stressed secondary-market yields suggest. The evidence does **not** establish that the entire >5GW buildout is already funded, that NVIDIA guarantees all debt, or that every loan is perfectly matched to its first customer contract.

The latest retrieved balance sheet is June 30, published August 12. Its balances are historical, expired for current-balance use under the project's 90-day convention. Subsequent August and September transactions are shown separately. **An exact October 22 debt balance is unavailable.** The SEC submissions index retrieved today was cached October 21; this is not an exhaustive real-time certification of today's filings. All material records, source dates, uncertainty and numeric assumptions are in [debt-stack.json](debt-stack.json).

## 1. Entire filed debt stack

June 30 instrument balances, **USD billions**, before the separately disclosed discount/issuance-cost deduction. Effective rates are rounded filing figures; cash coupons and quoted spreads are different measures.

| Instrument | Balance | Effective rate | Payment/rate structure | Maturity shown in Q2 |
|---|---:|---:|---|---|
| DDTL 1.0 | 1.300 | 15% | Floating; quarterly principal | March 2028 |
| DDTL 2.0 | 3.190 | 11% | Floating; quarterly principal from January 2026 | August 2030 |
| DDTL 2.1 | 3.000 | 9% | SOFR +4.25%; quarterly principal from July 2026 | March 2031 |
| DDTL 3.0 | 2.215 | 9% | SOFR +4.00%; monthly principal from April 2026 | August 2030 |
| DDTL 5.0 | 1.101 | 9% | SOFR +4.50%; monthly principal from November 2026 | November 2031* |
| 2030 senior notes | 2.000 | 10% | Fixed 9.250% cash coupon | June 2030 |
| 2031 senior notes A | 1.750 | 10% | Fixed 9.000% coupon | February 2031 |
| 2031 senior notes B | 2.750 | 10% | Fixed 9.750% coupon | October 2031 |
| 2032 USD senior notes | 1.250 | 10% | Fixed 9.625% coupon | July 2032 |
| 2032 EUR senior notes | 2.279 | 9% | Fixed 8.500%; USD amount from filing translation | July 2032 |
| 2031 convertible notes | 2.588 | 2% | Fixed 1.75% coupon; conditional conversion | December 2031 |
| 2032 convertible notes | 4.000 | 2% | Fixed 1.75% coupon; conditional conversion | October 2032 |
| Acquisition promissory notes | 0 | 7% historical effective rate | Settled in shares in April 2026 | Settled |
| Revolver | 0 | 7% | Floating; $2.5B commitment | November 2029 |
| Recourse OEM/software financing | 4.220 | 11% | Equipment/vendor arrangements; individual rate types not extracted | December 2026–July 2030 |
| Magnetar/MagAI obligation | 0.189 | 12% | Refundable capacity deposit plus redemption premium | January 2029 stated term |
| **Recourse subtotal** | **31.832** | | Parent obligations or parent guarantees | |
| DDTL 4.0 | 2.837 | 7% | Mixed floating/fixed project financing | March 2032 |
| Non-recourse OEM/software financing | 0.882 | 9% | Vendor financing | August 2026–August 2028 |
| **Non-recourse subtotal** | **3.719** | | Limited customary carve-outs remain | |
| **Total before discounts/costs** | **35.551** | | | |
| Less unamortized discounts/issuance costs | **(0.483)** | | $0.427B recourse + $0.056B non-recourse | |
| **Net carrying debt** | **35.068** | | **$7.513B current + $27.555B non-current** | |

Sources: [Q2 debt note, Note 10](https://www.sec.gov/Archives/edgar/data/1769628/000176962826000366/crwv-20260630.htm), [FY2025 debt note](https://www.sec.gov/Archives/edgar/data/1769628/000176962826000104/crwv-20251231.htm).

*DDTL 5.0's Q2 narrative expects final payment in **May 2031**, while its debt table lists **November 2031**. Both are preserved rather than silently reconciled. Its September 2026 **draw deadline is not a debt maturity**.

The EUR notes' original principal is EUR2B. The displayed USD2.279B is the filing's June translation, not today's FX. The EUR2B cross-currency hedge does not by itself disclose a synthetic all-in USD interest rate.

## 2. What changed after June?

| Completed/disclosed event | Amount and terms | What it establishes |
|---|---|---|
| August DDTL 5.5 | **$2.6B commitment; $1.2B drawn** disclosed by Q2 filing date. SOFR +5.50%; September 1, 2031 maturity | New project financing, not $2.6B already borrowed |
| August revolver draw | **$1.2B** | Parent liquidity funding under an existing facility; November 2029 stated maturity |
| September 22 convertible closing | **$4.2B issued**, including exercised $500M option; **2.875% coupon**, April 1, 2033 maturity | Low fixed cash coupon with equity optionality; final closed terms supersede preliminary presentation assumptions |

The September offering produced **$4.137B after initial purchaser discounts**, before other offering expenses. **$566.2M** funded capped calls, leaving **$3.5708B before other expenses**. Annual cash coupon is **$120.75M**. Initial conversion price is approximately **$97.85**; capped-call cap **$199.70**. The low coupon is obtained with equity optionality and upfront costs; it is not a guaranteed equity conversion or a 2.875% all-in economic cost.

An additive bridge is **$35.551B + $1.2B + $1.2B + $4.2B = $42.151B**, **before** post-June repayments, further draws, OEM financing and FX changes. This is **not today's balance**, a floor or a ceiling. A reported ~$50B headline cannot be reconstructed as exact funded debt from these documents alone.

Sources: [August 8-K](https://www.sec.gov/Archives/edgar/data/1769628/000176962826000357/crwv-20260807.htm), Q2 Note 16, [September closing 8-K](https://www.sec.gov/Archives/edgar/data/1769628/000176962826000432/crwv-20260917.htm).

## 3. Are short-term loans waiting to be converted?

**There are short-duration obligations; there is no evidence here of a single giant bridge that must be converted to finance the whole fleet.**

- The **$1B 2024 term loan was repaid April 11, 2025** after the IPO accelerated its maturity. It is not an outstanding 2026 refinancing cliff.
- **OEM equipment financing generally runs one to three years**, shorter than a seven-plus-year GPU economic-life assumption. It can be paid down from operations, refinanced or replaced by other capital; conversion is not mandatory by design. The filings do not supply every vendor tranche's repayment or refinancing plan.
- Acquisition convertible promissory notes were settled in stock in April 2026.
- The long-dated public notes principally mature in 2030–2033, though default/fundamental-change rights can accelerate obligations.
- **Current debt includes amortizing installments on longer loans.** The $7.513B current carrying amount should not be called $7.513B of short-term bullet loans.
- Magnetar is unusual: its redemption/termination rights can make cash obligations earlier than its stated term. FY2025 classified it current; June records a $100M payment and $189M remaining. Do not treat January 2029 as its only possible cash-call date.

June's scheduled principal ladder:

| Period | USD billions |
|---|---:|
| Rest of 2026 | 4.413 |
| 2027 | 6.184 |
| 2028 | 4.416 |
| 2029 | 2.421 |
| 2030 | 3.221 |
| Thereafter | 14.896 |
| **Total** | **35.551** |

This includes amortization, not just final maturities. First-half 2026 **actual repayments were $5.219B**. The cash obligation is real even when refinancing is unnecessary. These principal payments reduce cash available to shareholders but **do not reduce EPS as an expense**.

## 4. Does management tie financing to contract earnings?

**Yes. This is explicit, not merely an inference.** September's investor presentation describes asset financing secured by take-or-pay customer contracts, equipment and leases, drawn as costs are incurred, normally amortizing with customer payments so that initial contract cash flows repay the asset debt. Excess cash can flow to the parent, subject to financing restrictions. The parent funds the remaining capital needs through prepayments, stabilized cash generation, corporate borrowing, vendor finance, convertibles and equity.

The strongest concrete evidence is **DDTL 4.0**:

- **$8.5B committed**, with about $2.8B outstanding in June, not $8.5B funded.
- Floating pricing **SOFR +2.25%**; fixed pricing **blended Treasury +2.00%**.
- Borrowing limits reference eligible equipment cost, **projected debt-service coverage** and project conditions.
- Non-recourse to parent apart from customary carve-outs, secured on project assets/equity.
- Draws through June 2027 and maturity March 2032; monthly principal starts according to site/draw triggers.
- Restricted cash reserves protect debt service and operating costs; they are not freely distributable parent cash.

Management's [March illustration](https://s205.q4cdn.com/133937190/files/doc_presentations/2026/Mar/02/March-2026-Investor-Presentation.pdf) assumes **75% contract-level EBITDA margin, 80% loan-to-cost, 6.5% financing and a five-year contract/debt term, with no upfront customer prepayment**. It includes rent, power and direct operating expenses. These are valid **scenario inputs**, not proof every signed contract achieves them. Parent overhead, taxes and financing of the remaining capital still matter.

**The exception is deliberate:** DDTL 5.5 finances contracts averaging about **three years** with debt running about **five years**. Lenders accepted renewal/re-leasing risk, and management expects shorter contracts to command higher pricing. This supports both equipment residual value and potential repricing; it also leaves a genuine gap between initial contracted receipts and debt life. The facility requires **DSCR of at least 1.35x** starting after the specified commitment/date trigger. DSCR includes debt service under the agreement's definitions; do not substitute consolidated EBITDA/interest coverage.

Sources: [September presentation, slides 11 and 27](https://www.sec.gov/Archives/edgar/data/1769628/000176962826000429/crwv2026convertpresentat.htm), [DDTL 5.5 issuer description](https://investors.coreweave.com/news/news-details/2026/CoreWeave-Closes-2-6-Billion-Loan-Facility-Expanding-Financing-Flexibility-for-AI-Infrastructure/default.aspx), Q2 Note 10.

## 5. Rates, fees and what can actually reprice

Management showed weighted effective borrowing cost falling from **14.9% FY2023 → 12.2% FY2024 → 9.0% FY2025 → 8.3% Q2 2026**. That supports improving access as scale and collateral quality increased. Early DDTL 1.0 nevertheless still carried a rounded **15% effective rate**; early buildout funding was not uniformly cheap.

The September slide's **7.8% pro-forma** figure assumed a **$3.5B convertible at 2.625%** and excluded DDTL 5.5. Actual closing was $4.2B at 2.875%. **Do not call 7.8% today's verified weighted borrowing cost.** Likewise, DDTL 4.0's lower spread, DDTL 5.0's +4.50% and DDTL 5.5's +5.50% reflect different risk/contract structures; they are not one uniform financing curve.

Q2 debt cost bridge, USD millions:

| Item | Amount |
|---|---:|
| Contractual debt interest | 592 |
| Discount/issuance-cost amortization and redemption accretion | +45 |
| Capitalized interest | −79 |
| **Expensed debt-note interest** | **558** |
| **Consolidated interest expense, net** | **640** |

The difference includes other financing components; a complete $82M allocation is not supplied here. Capitalized interest is deferred into asset cost, not economically erased.

Undrawn fees are **0.50% annually** for DDTL 3.0/4.0/5.0/5.5 and **0.25%** for the revolver. DDTL 4.0 capitalized $151M financing costs and DDTL 5.0 $25M. Larger facilities increase fee dollars, but unused commitments are generally not charged the full drawn interest rate. Convertibles also involve discounts, capped-call spending and dilution exposure.

A secondary-market bond yield does **not** reset an existing fixed coupon. Exposure remains in:
1. Floating benchmark resets on unhedged principal.
2. Refinancing of maturing/amortizing balances if cash is insufficient.
3. New financing, including delivery/ramp funding after a customer price has been signed.
4. Renewal/re-leasing and covenant/collateral requirements.

June interest swaps had **$4.661B notional**. DDTL 3.0/4.0/5.0 require substantial hedge coverage, sometimes after future triggers. The Q2 risk factor still describes most variable-rate Credit Facility debt as **unhedged**. A future 95% hedge requirement is not evidence 95% of the entire debt stack is fixed today.

Q2 disclosed roughly **$30M quarterly interest sensitivity per +1 percentage point**. Annualizing gives **$360M for +3 points** on that June exposure. This is not a verified October net-of-all-hedges sensitivity.

## 6. Can premium pricing offset financing increases?

**Plausibly, particularly on new and renewing capacity. It cannot retroactively reprice all fixed backlog.** Common macro pressure on competitors supports the pricing thesis, but funding costs, power access and contract books differ.

Analyst sensitivities, not forecasts:

| Affected average debt | Rate increase | Extra annual interest |
|---|---:|---:|
| $10B | +3 percentage points | $300M |
| $20B | +3 percentage points | $600M |

With illustrative annual revenue of $26B, the cost is **1.15–2.31% of total revenue**. At 75% incremental contribution and all revenue repricable, the required premium is **1.54–3.08%**. If **only 25%** of revenue reprices that year, it is **6.15–12.31% on that slice**. A pure premium with unchanged operating cost can contribute closer to 100%, lowering the required price increase.

Model each deployment's billing start, cash receipts, equipment/debt cost, amortization, floating/hedged exposure and renewal window. Additional capacity brings revenue **and** debt service; recognize both for the months actually operating. Seven-plus-year equipment earning life can support cash after initial debt paydown, but does not remove principal repayment or prove renewal pricing.

## 7. Does NVIDIA support fund the entire >5GW?

The [January partnership](https://investors.coreweave.com/news/news-details/2026/NVIDIA-and-CoreWeave-Strengthen-Collaboration-to-Accelerate-Buildout-of-AI-Factories/default.aspx) discloses **$2B equity** and intended use of NVIDIA's financial strength to accelerate land, power and shell procurement for **more than 5GW by 2030**. September described this support as selective.

Disclosed operating footprint was **~1.5GW active at June 30** and **~4.2GW contracted power at August 11**. Contracted power is not fully equipped, energized, billable capacity. The framework and future agreements do not disclose an irrevocable financing amount covering all equipment, power, shells and parent capital through >5GW.

**Investment implication:** The financing model is more contract-linked and staged than a blanket “all debt must refinance at 15%” story. The outstanding questions are the near-term cash waterfall, vendor maturities, unhedged floating exposure, and the funding still needed between signed customer commitments and billable delivery—not an assumption that NVIDIA affiliation has already funded the entire buildout.

## 8. Other obligations and model boundaries

June also carried **$16.319B operating lease liabilities**, **$221M finance lease liabilities**, and **$9.692B deferred revenue**. Do not silently combine them into coupon debt or ignore them: rent is already included in operating margins, and customer prepayments are funding accompanied by service obligations and sometimes significant financing components.

Cash was **$5.524B**, securities **$15M**, restricted cash **$1.380B**. Reported facility availability was **$10.014B**, giving **$15.553B reported liquidity** including unrestricted cash/securities—not $15.553B of free cash.

A separate DCSP arrangement has $302M gross note receivable set off against $112M financing obligation and $118M finance lease, leaving a $72M net receivable. It carries 13–15% imputed/contractual rates. Preserve that setoff and avoid duplicating gross obligations in net debt.

**Coverage gaps:** October exact balances and hedges; each OEM tranche; customer-by-customer waterfalls; full 5GW funding schedule; DDTL 5.0 date discrepancy; latest default/covenant status after June. These remain explicit unknowns, not zero values. This report does not update canonical events, relationships, price feeds or valuation engines.

## Integrated traversal / divergence research

The maintained company-research entry is [divergence and debt repricing](divergence-and-repricing-2026-10-23.md), including the Friday Oct23 close refresh. Machine-readable traversal/compression observations: [Oct23 snapshot](traversal-compression-2026-10-23.json). The existing [factor tracker](factor_tracker.py) consumes dated matched-close fixtures; [Oct23 attribution](factor-attribution-2026-10-23.json) retains prior-window coefficients and daily residuals. Oct22 inputs and outputs remain immutable. These are repo-owned research outputs, not a separate app or external document system. Continuous ingestion/shared traversal integration remains [handoff #70](https://github.com/whiterosecoffee/_BASKET/issues/70); no persistent live refresh is claimed.

October dollar-turnover and downward-velocity history is integrated into the divergence research above; raw and calculated observations are in [October turnover/velocity](october-turnover-velocity.json).

## Functional tool transition

The [functional tool blueprint](functional-tool-blueprint.md) maps the full CRWV conversation into measurable components, proposed input/output contracts, valuation history, acceptance criteria and upstream-owner dependencies. The [new conversation prompt](next-conversation-prompt.md) starts an independently scoped implementation worker; it does not launch one or imply that live refresh exists. Both are specifications, not a deployed tool.

## Generic battle-band matrix prototype

[Calculator and matrix contract](battle-matrix-contract.md), [generic calculator](battle_matrix.py), [tests](test_battle_matrix.py), [dated cross-ticker inputs](matrix-input-2026-10-28.json), [CRWV/ORCL matrix](matrix-output-2026-10-28T1416Z.json), and [append-only snapshot history](battle-matrix-history.jsonl). Weighted up/down efficiency is centered on 1; band-assigned volume and ADV participation are separate. Twelve local tests passed. Delayed research fixture; automatic clustering and continuously scheduled refresh are not implemented. Shared adoption routes through #70.

## Traversal prior-art refinement

[Prior-art review](traversal-prior-art-review.md) compares eight families and distinguishes turnover efficiency from path progress, boundary events and predictive outcomes. Prototype v1.1.0 adds path/noise and ceiling-contact diagnostics; [dated v1.1 result](matrix-output-2026-10-28T1416Z-v1.1.0.json) preserves the original v1 result. Nineteen local tests pass; no prediction calibration, independent CI or live refresh is claimed. A ceiling untested during a decline is not described as a fresh rejection.
