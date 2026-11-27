# Holding-company economic moat and capital-conversion contract v0.1 (research design)

**Owner:** B09 / issue #300 / branch `work/300-sftby-capital-conversion-rotation`. **Status:** design-only; not a running engine, validated valuation, or authority to trade. **As-of:** 2026-11-26. Read root AGENTS.md, local AGENTS.md, state.json and feature-design.md first.

## Purpose and boundaries
Determine **incremental shareholder-attributable NAV and distributable parent cash per USD of new equity actually at risk**, while preserving the ability to meet debt, liquidity and collateral commitments. Report valuation effects, parent financing, execution timing and realizability separately. Do not conflate gross investee revenue, gross counterparty contract backlog, project AUM, consolidated accounting earnings, fund NAV, or share price with cash accessible to SoftBank.

Use preexisting B04 valuation and floating-rotation interfaces (issues #30/#297, PR #298), B13 OpenAI evidence (issue #26, PR #31), B09 OpenAI NAV bridge #28, B05 relationships, B02 FETCH/FX; never fork their implementations. The method may later be abstracted into _PATTERNS by its owner; no authority to edit _PATTERNS index from B09.

## Model layers (general parent -> SFTBY instance)
1. **Instrument and ownership tree:** SBG → SVF1/SVF2/other funds → holdings; SBG → Arm control interest; SBG → listed SoftBank Corp; SBG → SB Energy and DigitalBridge interests where verified. Each edge carries equity class, effective ownership, veto/control, pledge/collar/forward, fund fees/carry/waterfall, legal entity, source vintage, and realized/estimated status. A contract, guarantee or commercial partnership is an edge of a different type, NOT equity ownership.
2. **Operating engines:** Arm licenses, royalties, and new direct-silicon sales use separate margins and working-capital assumptions; OpenAI consumer/API/enterprise/agents separate gross vs net billed revenue, inference/training, equity compensation and cash burn; SB Energy signed, financeable, under-construction, commissioned, tenant-accepted, billed, collected and distributed capacity measured distinctly; telecom operating cash and parent dividends separately; robotics / direct stakes as options until monetization proven.
3. **Counterparty risk graph:** Record OpenAI as SBG investee and potential SB Energy tenant; NVIDIA as Arm ecosystem partner, SB Energy investor/compute supplier and conditional credit-support provider; NVDA's credit support is not interchangeable with cash, a blanket guarantee or wholly attributable SBG equity. Record collateral beneficiary and guarantee cap/milestones. Anthropic is a competitive comparator, not automatically a SoftBank asset. Capture model price-performance, enterprise retention, API unit economics, public valuation methodology and compute commitments for OpenAI-vs-Anthropic without inferring current IPO state.
4. **Valuation bridge:** Mark parent-attributable NAV at dated source prices; isolate price-change, FX, financing, dilution, new investment at cost, realization and holding-company discount. Replace embedded OpenAI mark inside SVF2 only via matched rights/vintage; never add gross stake valuation to fund NAV. Avoid duplicate SB Energy project NAV and backlog. Do not add operating profits to NAV if already capitalized in investment marks.
5. **Funding waterfall:** Start from reconciled legal-entity unrestricted cash and committed/uncommitted facilities; distinguish reported cash position, ring-fenced collateral, availability, covenants, undrawn lines and access rights. Forecast investment calls, funded projects, interest, amortization, equity contributions, distributions and guarantees quarterly. Parent debt is not identical to project-level nonrecourse debt.
6. **Capital optimization:** Compare hold vs sell-and-repay vs sell-and-redeploy and wait/stage/abandon for one identical point-in-time input snapshot. Model cash proceeds, market impact, taxes, fees, foregone returns, cost of debt, foregone optionality, and covenant/pledge constraints. Optimize only among feasible actions; no trade execution.
7. **Independent challenge:** Test downside alternatives, conflicting source dates and combined ARM/OpenAI/AI infrastructure stress. Falsifiers and missing evidence are first-class outputs; red-flag checks supersede numerical targets.

## Typed research contract (suggestion; B00 schema ownership)
Input object fields:
- `as_of`, `available_as_of`, `base_currency: USD`, `snapshot_id`, `source_manifest_hash`, `model_version`, `git_sha`;
- `entities[]` with legal ID, currency, reporting period, owner_fraction, security class, fund net entitlement, value basis, pledge/forward/lockup, source and timestamp;
- `economic_edges[]` with `equity|customer|supplier|lease|guarantee|loan|strategic|competitor`, legal parties, bilateral cash-flow treatment and disclosure vintage;
- `operating_cases[]` with revenue/cost units, recognition gate, probability-free state, margins, capex, maintenance, taxes, cash distributions, competitive-moat falsifiers;
- `finance_schedule[]` including loan obligor/recourse, pledged units, collateral triggers (nullable), commitment, drawn amount, interest, amortization, restricted/unrestricted cash, maturities, contract rights;
- `actions[]` hold/sell/repay/reinvest/defer, and explicit transaction costs, slippage, tax, foregone growth;
- `scenarios[]` with correlated shocks and source-qualified assumptions.

Output object fields:
- `qualification`: `verified|provisional|blocked`, missing fields, stale/conflicted observations, coverage;
- `nav_bridge[]`: attributable USD NAV, separate financing/restrictions, no duplicate positions, source date;
- `quarterly[]`: accessible cash, liquidity headroom, qualified investment commitments, collateral facility coverage and UNKNOWN thresholds, group LTV, lender-specific LTV, covenants, accepted/billable/collected MW, parent distributions;
- `capital_conversion[]`: new parent cash committed, discounted attributable incremental cash flows, realizable NAV delta, transaction friction, `incremental_npv_per_dollar`, `incremental_nav_per_dollar`, counterfactual hold value;
- `risk[]`: correlated edge exposures, concentration, downside liquidity/forced-sale flags;
- `review`: evidence citations, falsifiers, unresolved assumptions, scenario version and disposition. Unknown values are null, never zero.

### Economic-value identity
For a new project: `incremental_NPV = PV(ownership-adjusted future distributable cash + terminal realization) - PV(all new parent cash calls) - tax/friction - incremental financing cost` (avoid counting financing twice in discount rate and cash flow). `NAV_created_per_new_parent_dollar = attributable_incremental_NPV / PV(parent_cash_at_risk)`; report denominator and null when zero or missing. Economic profit `NOPAT - WACC * invested_capital` is a separate operational diagnostic. A debt repayment can improve liquidity/discount while producing zero immediate accounting NAV gain. A market-mark increase is not cash generated by the new project.

## Moat-specific evidence and falsifiers
- **Arm IP:** architecture lock-in, ecosystem, licensing/royalties, custom silicon conflict. Test pricing/royalty per chip, license renewals, chip ASP/margins, R&D and stock compensation, competing ISA substitutes. Direct silicon must never inherit 97%-style IP gross margin.
- **OpenAI vs Anthropic:** enterprise workflow lock-in, retention, model quality/cost per successful task, multi-model substitution, usage vs recognized revenue, inference gross margin vs full operating margin, stock compensation, training capex, compute commitments, dilution. IPO planning is a contingent catalyst; never assume filing/price/lockup status without a dated primary record. Compare the same revenue and cost definitions and public/private valuation stages.
- **SB Energy + NVIDIA:** grid interconnection/site scarcity, 15–20 year lease protection and escalators versus construction risk, concentration in OpenAI/affiliate tenants. For PORTS-Pike NVIDIA source describes exclusive AI compute infrastructure provider, initial 4.25 IT-GW conditional land/power/shell credit support, option for remaining 3.75 IT-GW, and $1.5B investment; verify the contract scope and do not count support as rent, NAV or fungible collateral. Stage sequence: signed → financed → power confirmed → completed → accepted → billable → collected → cash distributed. Source: https://www.sec.gov/Archives/edgar/data/1045810/000104581026000069/sbeoainvidia-portsrelease.htm (2026-08-17).
- **SoftBank Corp and DigitalBridge:** subscriber churn, enterprise AI distribution, dividend upstreaming, telecom capex, third-party AUM versus manager equity and fee-related earnings.
- **Physical AI:** robotics unit economics, repeat customers, uptime, safety and serviceability, legally completed acquisitions versus announced transactions.

## Minimum focused tests before promotion
T1: one OpenAI exposure embedded SVF2 then repriced; gross equity addition fails.
T2: NVIDIA conditional guarantee recorded as risk mitigation only, not cash or SBG equity.
T3: $439B SB Energy backlog with 0 operational GW yields 0 accepted/billed data-center revenue.
T4: equal-value sale and debt repayment leaves NAV unchanged before costs; liquidity and LTV change only under correct debt classification.
T5: margin call with unknown threshold returns `blocked`, not a fabricated ARM strike.
T6: identical hold/rotate inputs; add tax, spreads and missed rebound; rotation may change sign.
T7: two dates and FX sources mismatched; current NAV blocks.
T8: OpenAI/Anthropic comparisons disallow gross-vs-net revenue mismatch and unverified IPO event promotion.
T9: correlated OpenAI loss simultaneously affects SVF2 mark, affiliated SB Energy tenant, parent guarantee and liquidity; no double-subtraction.
T10: a 25%/35% group LTV boundary triggers scenario action/violation and cannot present impossible unattended financing path as viable.
T11: historical replay cannot use events first available after scenario date.
T12: negative parent free cash despite rising gross revenue retains a negative NAV-alpha output and stress flag.

## Microsoft-style operating approach
Prefer one owner-scoped deterministic workflow (qualification → graph → operating submodels → NAV/cash waterfall → alternatives → review) and small specialist research skills for ambiguous evidence, not a new multiagent controller. Typed inputs, checkpointed snapshots and expected-output fixtures; stop on stale/unknown financing gates. Separate tool permissions from analysis; no orders or merges. Route changes in shared schemas to B00, engine implementations to B04, cross-domain validation to B01, ownership/edges to B05 and current price/FX to B02. Trace input source availability, executor/model versions and human approval.

Reference guidance: https://learn.microsoft.com/en-us/agent-framework/journey/workflows ; https://learn.microsoft.com/en-us/agent-framework/workflows/checkpoints ; https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluate-agent

## Accessibility / publishing proposal (unexecuted)
_ PATTERNS root Snapshot.json already resolves published components by receipts. Its owner may add a registered `_ECONOMIC_VALUE_INTELLIGENCE` feature node, with `AGENTS.md`, `state.json`, feature-design for typed contract, and pointer to B09 this branch and B04 engines. No duplicate spreadsheet or code. B09 cannot edit _PATTERNS root index under _BASKET authority. 
Use `SFTBY_CAPITAL_CONVERSION` as B09-specific child. Do not claim registered, received, or merged without corresponding GitHub evidence.

## Acceptance for this document
This is source-qualified *architecture design*, not proof of a functioning evaluator. Only code with deterministic tests, actual runner outputs, independent review and reconciled legal-entity finance data may claim production valuation.
