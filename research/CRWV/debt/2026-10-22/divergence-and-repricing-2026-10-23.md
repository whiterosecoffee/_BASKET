# CRWV divergence and debt repricing baseline — 2026-10-23

Research on B10 / issue #68 / draft PR #69. Daily price data end 2026-10-22; no current intraday quotation. USD throughout.

## Reproducible attribution

`factor-closes-2026-10-22.csv` is a dated research fixture of 203 matched closes from Massive daily aggregates, retrieved 2026-10-23. It is not canonical B02 ingestion. Endpoint: `/v2/aggs/ticker/{ticker}/range/1/day/2026-01-01/2026-10-22`, adjusted=true by default. Exact provider revision/first-available timestamps unknown. No future or incomplete session included.

Run `python factor_tracker.py [input_csv] [new_dated_output_json]` (numpy required). Keep prior dated inputs/outputs; generate a new dated revision when refreshing. Never overwrite historical observations silently.

Models: QQQ only; QQQ plus NVDA jointly; all five factors jointly. Fit each day using only the preceding 60 completed return observations. Price returns rather than total returns. Outputs retain beta weights, intercept, standardized effects, individual factor contributions, actual/conditional expected returns, residual, residual/training sigma, R-squared, conditioning and all daily records. Betas are not portfolio allocations and need not sum to one.

QQQ includes NVIDIA; jointly estimated NVDA loading is incremental exposure after QQQ. Do not sum standalone regressions. HYG is an imperfect credit proxy (duration/distributions); IEF is a Treasury price proxy, not SOFR; USO includes oil-futures roll effects, not Brent spot. A negative IEF loading can reflect flight-to-safety conditions. No causal interpretation or trading probability is assigned.

All 142 walk-forward records use same-day factor observations, so this is ex-post attribution with prior-fitted coefficients, not an advance return forecast. Residual is unexplained performance, not proven alpha or credit news. Missing any required close blocks calculation. Prefix replay and contribution-conservation assertions passed. Independent exact-head CI not verified.

## Recent divergence (percentage points)

| Date | Actual CRWV % | QQQ+NVDA conditional % | Residual pp |
|---|---:|---:|---:|
| 2026-10-13 | -3.05 | -1.18 | -1.87 |
| 2026-10-14 | -15.46 | -7.55 | -7.91 |
| 2026-10-15 | 5.94 | -1.08 | +7.02 |
| 2026-10-16 | -11.91 | -10.10 | -1.81 |
| 2026-10-19 | -0.44 | 4.53 | -4.97 |
| 2026-10-20 | 1.65 | -0.81 | +2.46 |
| 2026-10-21 | -0.50 | 3.76 | -4.26 |
| 2026-10-22 | -10.06 | -11.49 | +1.43 |

## Comparative model error

- market: walk-forward RMSE 5.144 percentage points across 142 observations.
- market_ai: walk-forward RMSE 5.137 percentage points across 142 observations.
- five_factor: walk-forward RMSE 5.247 percentage points across 142 observations.

Zero-return baseline RMSE is 5.927 percentage points. Five-factor model does not outperform the simpler market/AI baseline over this sample. Preserve it as a diagnostic, not a validated upgrade. This is an exploratory model comparison, without independent model-selection holdout. Live industry comparison should add an independently specified neocloud/AI-infrastructure peer basket through the appropriate owner; QQQ/NVDA alone are market/AI proxies.

## Debt and customer economics

Full instrument map is in `debt-repricing-2026-10-23.json`, derived from the prior sourced debt audit. June principal schedule totals $35.551B; carrying debt after $483M costs/discounts is $35.068B. Current debt carrying amount $7.513B is not identical to remaining-calendar-2026 principal ($4.413B). Scheduled amortization is not automatically a refinancing requirement.

The June fixed senior note/convertible categories total $16.617B before the separately reported discount line (46.7% of gross scheduled debt). EUR note is retained at filed USD translation; swaps determine its synthetic USD cash cost. Subsequent $4.2B 2.875% convertible issue is recorded separately, not simply added to claim current debt. Original cash coupons and effective accounting rates differ.

Favorably priced examples include DDTL 4.0 at SOFR+225bp or Treasury+200bp and 1.75% convertible coupons. They are not representative of every initial loan: June DDTL1 effective rate was approximately 15%. DDTL5.5 later had SOFR+550bp. Rates reflect different collateral, contracts, structures and dates, not a uniform issuer borrowing rate.

Existing fixed coupons do not rise with traded yields. Floating benchmarks can reset without renegotiation, offset by executed hedges. DDTL3/4/5 hedge requirements must not be mistaken for complete current hedge coverage. New borrowing, amendments and refinancing can reset spreads/fees/covenants; undrawn commitments may retain contracted spreads but their conditions and benchmark fixing still matter.

New customer pricing can incorporate higher funding costs. Issuer evidence of July price increases and higher-priced short contracts supports pricing capacity. It does not establish an automatic financing-cost escalation clause on every service contract. Distinguish new unpriced work, signed revenue with undrawn funding, live funded contracts, renewals and refinancing of aging equipment. Match revenue and debt by cohort before claiming margin protection.

For each $10B affected principal, +100bp means $100M annual pre-tax interest before hedges. Required annual customer revenue uplift = incremental net interest / incremental contribution margin, plus relevant fees, operating cost and equity-return requirements. Example: $100M / 80% = $125M, explicitly a scenario. Do not apply stressed bond yields to all debt or to operating leases.

## Integration handoff

No continuous updater has been deployed. B02 owns entitled daily price ingestion; B06 owns shared traversal; B00 must route integration. Required input: dated complete closes for six tickers, adjustment convention, revision, observed/available/ingested timestamps. Required output: dated factor results, coefficients and training window, divergence history, missing/stale status and immutable prior revisions. Credit requires same-instrument spread/CDS observations plus SOFR, hedge notional/maturity and repayment/draw events. Customer cost-pass-through remains unknown until verified.

## Debt obligations

June balances below are USD millions before separately reported discounts. These are historical balances, not October exposure.

| Instrument | Balance | Contract terms / maturity | Repricing |
|---|---:|---|---|
| DDTL 1.0 | 1,300 | Up to 2300 original commitment; quarterly amortization; final payment March 28, 2028. Contract spread not independently extracted. Maturity: Mar 2028. | Benchmark can reset under existing agreement without renegotiation. Contractual spread does not automatically follow traded bond spread. Net exposure depends on executed hedges and floors. |
| DDTL 2.0 | 3,190 | Up to 7600 commitment; quarterly installments began January 2026; final payment five years after funding. Maturity: Aug 2030. | Benchmark can reset under existing agreement without renegotiation. Contractual spread does not automatically follow traded bond spread. Net exposure depends on executed hedges and floors. |
| DDTL 2.1 | 3,000 | Separate 3000 tranche, not another 7600; SOFR+4.25%; quarterly installments began July 2026. Q2 supersedes FY25 maturity label. Maturity: Mar 2031. | Benchmark can reset under existing agreement without renegotiation. Contractual spread does not automatically follow traded bond spread. Net exposure depends on executed hedges and floors. |
| DDTL 3.0 | 2,215 | 2600 facility; SOFR+4.00%; monthly installments began April 2026; 0.50% undrawn fee. Required hedge >=75% anticipated floating loans; FY25 stated compliance. Maturity: Aug 2030. | Benchmark can reset under existing agreement without renegotiation. Contractual spread does not automatically follow traded bond spread. Net exposure depends on executed hedges and floors. |
| DDTL 5.0 | 1,101 | 3100 facility, SOFR+4.50%; draw period ended September 30, 2026; installments start November 2026. Narrative expects final payment May 2031 while debt table lists November 2031: unresolved distinction. 0.50% undrawn fee; >=95% anticipated floating hedge required. Maturity: Nov 2031. | Benchmark can reset under existing agreement without renegotiation. Contractual spread does not automatically follow traded bond spread. Net exposure depends on executed hedges and floors. |
| 2030 senior notes | 2,000 | 9.250% cash coupon; senior unsecured; June 1, 2030 maturity. Maturity: Jun 2030. | No coupon reset from secondary-market yield changes. Refinancing/new issuance reprices; conversion, FX hedges and optional repayment require separate treatment. |
| 2031 9.00% senior notes | 1,750 | 9.000% cash coupon; senior unsecured. Effective rate rounded by filing differs from coupon. Maturity: Feb 2031. | No coupon reset from secondary-market yield changes. Refinancing/new issuance reprices; conversion, FX hedges and optional repayment require separate treatment. |
| 2031 9.75% senior notes | 2,750 | 9.750% coupon; senior unsecured; October 1, 2031 maturity; $27M issuance costs at issuance. Maturity: Oct 2031. | No coupon reset from secondary-market yield changes. Refinancing/new issuance reprices; conversion, FX hedges and optional repayment require separate treatment. |
| 2032 9.625% senior notes | 1,250 | 9.625% coupon; senior unsecured; July 15, 2032; $20M debt discount and issuance costs. Maturity: Jul 2032. | No coupon reset from secondary-market yield changes. Refinancing/new issuance reprices; conversion, FX hedges and optional repayment require separate treatment. |
| 2032 EUR senior notes | 2,279 | 8.500% coupon; original EUR2000M principal; filing USD carrying translation retained rather than new spot FX. Cross-currency swap covers EUR2000M; no assumed all-in synthetic USD rate. $41M issuance costs. Maturity: Jul 2032. | No coupon reset from secondary-market yield changes. Refinancing/new issuance reprices; conversion, FX hedges and optional repayment require separate treatment. |
| 2031 convertible senior notes | 2,588 | 1.75% cash coupon; senior unsecured; $57M issuance costs at issuance. Equity conversion optional/conditional, not guaranteed principal extinguishment. Maturity: Dec 2031. | No coupon reset from secondary-market yield changes. Refinancing/new issuance reprices; conversion, FX hedges and optional repayment require separate treatment. |
| 2032 convertible senior notes | 4,000 | 1.75% coupon; October 1, 2032; $70M discount/issuance costs, $492M capped-call outlay; initial conversion $119.60, cap $230. Capped-call spending is not recurring coupon. Maturity: Oct 2032. | No coupon reset from secondary-market yield changes. Refinancing/new issuance reprices; conversion, FX hedges and optional repayment require separate treatment. |
| Acquisition convertible promissory notes | 0 | $172M principal settled in shares in April 2026 at $106.61 conversion price; no remaining balance. Maturity: Apr 2026. | Settled balance; no remaining rate sensitivity. |
| Revolver | 0 | 2500 commitment; previous balance repaid April 2026; 533 letters of credit consume availability; about 2000 remaining June capacity. 0.25% undrawn fee. August 1200 draw belongs in overlay. Maturity: Nov 2029. | Benchmark can reset under existing agreement without renegotiation. Contractual spread does not automatically follow traded bond spread. Net exposure depends on executed hedges and floors. |
| OEM/software financing, recourse | 4,220 | Secured equipment/vendor financing; exact fixed/floating tranche split not extracted. OEM agreements generally one to three years; software generally less than five. Not all this balance is a short-term bullet. Maturity: Dec 2026–Jul 2030. | Unknown tranche-level rate reset and repayment schedule; do not classify all as fixed or floating. |
| Magnetar/MagAI obligation | 189 | In-substance debt from refundable capacity prepayment with termination-for-convenience rights; $100M paid June 2026. FY25 classified current despite later stated term: do not equate term date to cash-call date. Maturity: Jan 2029. | Contractual premium/cash-call terms govern; not a floating credit-spread reset. |
| DDTL 4.0 | 2,837 | 8500 facility; SOFR+2.25% or blended Treasury+2.00%; about 1400 floating/1500 fixed at June (rounded). Draw deadline June 30, 2027; 0.50% undrawn fee. Monthly principal commencement depends on draw/site events. >=95% anticipated floating hedge required after specified future dates. $151M capitalized financing costs. Maturity: Mar 2032. | Split fixed and floating tranches; benchmark sensitivity only on unhedged floating exposure. Hedge mandate is not evidence of current hedge notional. |
| OEM/software financing, non-recourse | 882 | Shorter vendor obligations included. Filing says short-term OEM debt weighted-average rate 9%; it does not disclose separate short-term-only balance here. Maturity: Aug 2026–Aug 2028. | Unknown tranche-level rate reset and repayment schedule; do not classify all as fixed or floating. |

## Sources

- [Q2 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1769628/000176962826000366/crwv-20260630.htm)
- [FY2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/1769628/000176962826000104/crwv-20251231.htm)
- [September 2026 investor presentation](https://www.sec.gov/Archives/edgar/data/1769628/000176962826000429/crwv2026convertpresentat.htm)
- [September convertible closing 8-K](https://www.sec.gov/Archives/edgar/data/1769628/000176962826000432/crwv-20260917.htm)
- [DDTL 5.5 credit agreement summary 8-K](https://www.sec.gov/Archives/edgar/data/1769628/000176962826000357/crwv-20260807.htm)
- [DDTL 5.5 closing announcement](https://investors.coreweave.com/news/news-details/2026/CoreWeave-Closes-2-6-Billion-Loan-Facility-Expanding-Financing-Flexibility-for-AI-Infrastructure/default.aspx)
- [NVIDIA/CoreWeave expansion announcement](https://investors.coreweave.com/news/news-details/2026/NVIDIA-and-CoreWeave-Strengthen-Collaboration-to-Accelerate-Buildout-of-AI-Factories/default.aspx)
- [DDTL 5.0 closing announcement](https://investors.coreweave.com/news/news-details/2026/CoreWeave-Closes-3-1-Billion-Loan-Facility-Expanding-Access-to-Public-Markets-for-GPU-Backed-Financing/default.aspx)
- [March investor presentation](https://s205.q4cdn.com/133937190/files/doc_presentations/2026/Mar/02/March-2026-Investor-Presentation.pdf)
- [Higher-priced short contracts, Sept 17](https://investors.coreweave.com/news/news-details/2026/CoreWeave-Continues-to-Contract-New-Compute-Capacity-at-Higher-Prices/default.aspx)

## Friday close refresh: traversal and market compression

Supersedes earlier intraday levels for Oct 23. Massive daily close $54.235, down 2.455%; regular session range $54.01-$56.11. Latest retrieved after-hours bar 19:56 ET closed $54.00, separate from regular close. Regular minute bars sum 41.737M shares and $2.287B notional, VWAP $54.801. Provider daily volume 46.943M is a different aggregation scope; do not mix it with regular-session minute volume.

Lower floor $54.07 broke at 15:56, new regular low $54.01. Lower monitoring band becomes $54.00-$54.15; this is tested but vulnerable, not confirmed support. $53.50 remains prior-day low, not touched Friday regular session. $54.75-$54.90 is the volume/VWAP pivot; $55.25-$55.35 remains the repeated upper band. $55.58-$55.62 and $56.02-$56.11 were opening-period zones, not repeatedly reached later.

Retrospective traversals from $54.07-$54.15 to $55.25 before a low below $54.07: 09:33→09:39 (6m), 10:17→10:41 (24m), 11:13→12:04 (51m); late 15:55→15:56 failed. Three completions in four attempts, selected retrospectively from one day; not a 75% forward success rate. Median successful traversal 24m; worsening speed before late failure. Minimum price distance from upper edge of lower band to target is $1.10, ~2.03%, before fills/costs.

| VWAP price bin | Whole-minute shares M | Whole-minute notional USD M |
|---|---:|---:|
| 54.00-54.25 | 3.097 | 167.8 |
| 54.25-54.50 | 7.868 | 427.8 |
| 54.50-54.75 | 9.141 | 499.3 |
| 54.75-55.00 | 10.189 | 559.0 |
| 55.00-55.25 | 5.737 | 316.2 |
| 55.25-55.50 | 2.094 | 115.9 |
| 55.50-55.75 | 2.140 | 119.0 |
| 55.75-56.00 | 1.472 | 82.2 |

All-bin sum reconciled to regular-session totals. Minute assignment is an approximation, not trade-level volume profile.

### How much macro compression is already reflected?

FactSet indexed primary-source reports: S&P500 forward P/E 20.4 at June30, 19.1 in Oct9 report, 18.7 in Oct23 report. Thus -8.33% since June and -2.09% since Oct9. Latest report also compares 19.0 at Sept30: -1.58%. These report-date observations need not match Friday's exact close. Forward denominator rolls and estimates change; this is observed multiple compression, not a causal rate decomposition. Restoring 19.1 from18.7 at unchanged earnings means +2.14%; restoring20.4 means +9.09%. Neither implies the same CRWV equity change.

From Oct9 close through Oct23: CRWV -33.92%, QQQ -6.24%, NVDA -7.99%, SPY -2.39%. Broad-market multiple compression alone cannot quantitatively account for CRWV's entire move.

For the sharp breakdown Oct13→Oct23, CRWV -30.30%, QQQ -5.27%, NVDA -7.68%. Freeze joint QQQ/NVDA coefficients using only data through Oct13: 60-session factor-only compounded association -19.29%, versus actual -30.30%, an arithmetic gap11.01pp; actual divided by conditional gross performance is -13.63%. Model including historical intercept gives -20.26%; drift must not be mislabeled macro effect.

Window sensitivity is large: 20-session pre-breakdown fit associates -8.06%, 120-session fit -11.94%. Thus approximately 8-19 percentage points of the30.3% decline are associated with common market/AI moves across these selected specifications, roughly27-64% in arithmetic decline units. This is model sensitivity, not a confidence interval, causal attribution or proof that remaining risk is priced in. QQQ itself includes AI-related financing fear; shared factors can carry the same narrative. The remaining11-22pp cannot be automatically assigned to credit or called an upside opportunity.

Friday actual -2.455%, rolling QQQ/NVDA conditional -0.360%, residual -2.095pp (only -0.424 training residual sigma). Material percentage-point underperformance but not statistically extreme for this volatile stock.

CRWV's own forward P/E compression cannot be established without matched positive forward EPS estimates at both endpoints. Assess enterprise-value/forward cash earnings with an explicit debt bridge; do not apply the distressed bond yield to fixed coupons or lease liabilities.

Sources and machine-readable calculations: `traversal-compression-2026-10-23.json`; updated matched daily inputs and rolling attribution in `factor-closes-2026-10-23.csv` and `factor-attribution-2026-10-23.json`. Existing historical files are retained.

## October dollar turnover and downward velocity — through October 23

Source: Massive daily aggregates retrieved after Oct23 session. September30 close $87.12 is the month-return anchor. Seventeen completed October sessions: 968.292M shares, estimated gross transaction notional $65.398B, combined VWAP $67.539; close $54.235, down37.747%. Float-turnover estimate2.95x uses provisional328.32M Yahoo float; this is not unique shares or owners. Daily volume scope is kept consistent; no mixing with intraday regular-only volume.

| Date | Close USD | Daily return | Shares M | Turnover USD B | Daily VWAP USD |
|---|---:|---:|---:|---:|---:|
| 10-01 | 88.570 | +1.66% | 20.46 | 1.78 | 87.07 |
| 10-02 | 89.620 | +1.19% | 23.59 | 2.13 | 90.28 |
| 10-05 | 87.390 | -2.49% | 18.24 | 1.60 | 87.94 |
| 10-06 | 91.720 | +4.95% | 32.05 | 2.93 | 91.29 |
| 10-07 | 88.450 | -3.57% | 19.91 | 1.76 | 88.53 |
| 10-08 | 81.580 | -7.77% | 42.32 | 3.50 | 82.81 |
| 10-09 | 82.080 | +0.61% | 20.01 | 1.65 | 82.26 |
| 10-12 | 80.260 | -2.22% | 19.02 | 1.52 | 80.13 |
| 10-13 | 77.810 | -3.05% | 34.41 | 2.67 | 77.46 |
| 10-14 | 65.780 | -15.46% | 111.21 | 7.41 | 66.61 |
| 10-15 | 69.690 | +5.94% | 130.54 | 8.43 | 64.59 |
| 10-16 | 61.390 | -11.91% | 95.39 | 5.97 | 62.60 |
| 10-19 | 61.120 | -0.44% | 101.01 | 6.26 | 62.00 |
| 10-20 | 62.130 | +1.65% | 94.78 | 5.83 | 61.53 |
| 10-21 | 61.820 | -0.50% | 76.59 | 4.72 | 61.65 |
| 10-22 | 55.600 | -10.06% | 81.76 | 4.65 | 56.85 |
| 10-23 | 54.235 | -2.46% | 46.98 | 2.58 | 54.86 |

| Phase | Net return | Dollar velocity per session | Geometric rate per session | Shares M | Turnover USD B | VWAP |
|---|---:|---:|---:|---:|---:|---:|
| 10-01 to 10-07 | +1.53% | +0.27 | +0.30% | 114.25 | 10.20 | 89.31 |
| 10-08 to 10-13 | -12.03% | -2.66 | -3.15% | 115.77 | 9.34 | 80.68 |
| 10-14 to 10-16 | -21.10% | -5.47 | -7.60% | 337.15 | 21.81 | 64.69 |
| 10-19 to 10-21 | +0.70% | +0.14 | +0.23% | 272.38 | 16.82 | 61.74 |
| 10-22 to 10-23 | -12.27% | -3.79 | -6.34% | 128.74 | 7.23 | 56.12 |

Interpretation: first October8-13 deterioration preceded the volume shock. October14-16 lost21.10% at -$5.47/session on337.15M shares. October19-21 temporarily stabilized (+0.70%) despite272.38M shares, about83% of provisional float. October22-23 then broke lower (-12.27%) at -$3.79/session on128.74M shares. The high-turnover plateau did not establish durable support.

Dollar velocity slowed31% between the two sharp selloff phases, but normalized geometric decline only eased from7.60% to6.34% per session. Daily share volume fell43%; price decline per100M shares worsened from$4.87 to$5.89 (~21%). This ratio is descriptive, not signed flow, market depth or causal impact. Lower volume does not by itself establish absorption.

Friday versus Thursday: absolute daily loss fell from$6.22 to$1.365 (78% smaller), volume from81.76M to46.98M (43% lower), and turnover from$4.65B to$2.58B. Friday close was only10.7% above the bottom of its day's range and1.14% below daily VWAP. Late regular low54.01: deceleration present; exhaustion unconfirmed.

Trading-weighted period prices descend89.31→80.68→64.69→61.74→56.12; Friday54.86. These are turnover reference points, not current holder acquisition prices. Supply-absorption evidence would require low tests with reduced downside displacement, higher lows and closes holding above current VWAP, confirmed against AI peers.

Five-session dollar velocity improved -$4.14/session Oct16 to-$0.79 Oct21, deteriorated to-$2.82 Oct22, then eased to-$1.43 Oct23. Rolling comparisons have window-roll effects: Friday drops the Oct16 -11.91% session from the five-day window, so improvement is not entirely new buying.

Machine-readable raw observations, daily calculations, phase calculations and rolling history: `october-turnover-velocity.json`. Formulae: turnover=volume*VWAP; dollar velocity=(ending close-starting close)/sessions; normalized velocity=(ending/starting)^(1/sessions)-1. Down-session volume646.86M is66.8% of total, but not classified sell-initiated volume.
