# OpenAI 2027 IPO — expanding the valuation evidence system
**B13 research, 2026-10-17; candidate under issue #26 / draft PR #31.** Status: methodology + source-readiness audit, not a B02 ingestion runtime, B04 valuation service or B09 parent NAV.

## Design correction: separate three processes

1. **Observe and verify**: regulatory filings, actual transactions, the issuer's attestations, normalized historical data; record exact source, instrument, unit, period, effective/available/observed/ingested and TTD. Conflicts are not averaged away.
2. **Estimate economics** (B04-owned): user-declared scenarios/real source fundamentals → revenue cohorts, retained FCF, training asset lifecycle, compute unit costs, capital stack and security-class waterfall → DCF/EV-to-equity values with versioned sensitivities. No objective "factor score" is directly multiplied by company value.
3. **Prioritize measurement** (B13 policy): importance weights decide *which facts to research*, not the dollar valuation. Evidence acquisition priority should eventually be proportional to valuation elasticity × material uncertainty × source access feasibility, measured rather than invented.

A fourth post-pricing process belongs to B06/B07: compare listed IPO offer/aftermarket against B04 point-in-time valuation and calibrate factor effectiveness on realized results. **No IPO price or return probabilities until this walk-forward evidence exists.**

## Provider audit — verified usable vs proposed

- **SEC filings / XBRL — newly tested on 2026-10-17** through connected Firecrawl Alexandria `sec-gov/filings/company`, `filings/filings`, `filings/concept`. CRWV resolved to CIK 0001769628; 8-K filing index returned Sep 17/22; MSFT XBRL `RevenueFromContractWithCustomerExcludingAssessedTax` returned **$331.839B** for FY ended 2026-06-30 (filed 2026-07-29); the additional Q3 record was **year-to-date** `2025-07-01→2026-03-31`, *not* a stand-alone fiscal quarter. This is a working **research connection**, not a continuously running B03 EDGAR adapter. A confidential OpenAI S-1 cannot be inferred from this endpoint.
- **Massive Treasury — tested on 2026-10-17**: `/fed/v1/treasury-yields` returned completed daily observations through Oct 15 (e.g. 10-year 5.10%). This is a reference discount-rate input, **not an OpenAI borrowing rate**. No ongoing worker or archive proven.
- **Massive public issuer financials — tested NOT_ENTITLED**: `/stocks/financials/v1/income-statements` for MSFT returned `NOT_ENTITLED`. Use SEC primary XBRL as fallback; optionally review provider entitlement, but no plan purchase is assumed.
- **Massive IPO reference — endpoint discovered only**: first invocation had an invalid sorting request; entitlement/functionality remains unconfirmed. Do not claim it lists or prices any private IPO.
- **Hyperliquid HIP-3 — documented but not ingested**: `POST /info` `metaAndAssetCtxs`, `fundingHistory`, verified deployer-specific universe, funding, mark, oracle, open interest; add L2 depth and liquidation controls. It is a **speculative derivative** not a security transaction or equity fair-value appraisal.
- **FRED/ICE OAS — publicly documented, adapter untested**: use IG/HY index spreads for macro financing regimes; individual CoreWeave or SoftBank debt still requires deal-specific CUSIP, price, collateral, maturity and spread from an entitled provider.
- **Direct private equity secondaries — no verified transaction feed**: do not infer an IPO price from published rumors or derivative indices; require trade date, security class, issuer capitalization, transferred shares, settlement, block size, restrictions and actual net transaction price.
- **Independent product adoption/traffic — optional**: Similarweb or verified enterprise surveys can monitor competitive interest; web traffic is not paid usage, API consumption or GAAP revenue. Priority P2, never use to replace audited issuer metrics.

Full factor, priority, owner, access, fallback and missing-field mapping: `resource-registry.json`. Offline `resource_audit.py` can print date-fixed research source acquisition priorities for the baseline and hypothetical credit-stress weights. It **does not query providers**.

## Expected measurement expansion

| Measurement | Gold-standard field | Source | Current release gate |
|---|---|---|---|
| Issuer value | Transaction share class + fully diluted capitalization + as-of | completed security financing, S-1, verified secondaries | B00 #29, B13 record |
| Revenue | Quarterly GAAP direct, API, enterprise and channel gross/net with basis | public S-1 when filed; issuer release until then provisional | B03 event, B04 normalization |
| Growth quality | Retention, consumer conversion, enterprise revenue concentration, distribution margin | audited customer/service disclosures, issuer, qualified survey | unknown until independently disclosed |
| Compute economics | $/delivered workload, utilization, net gross margin by inference vs training, depreciation useful life | issuer financials, vendor filings, contract terms | B04 bounded assumptions, not supplier extrapolation |
| Funding | cash available, cash burn, prepayments/restricted cash, debt, compute minimum payments, equity dilution timing | audited cash flow, financing, agreements, issuer/SEC | B04 EV↔equity bridge blocked |
| Competitive dynamics | Anthropic actual prospectus/IPO comparables; principal-agent normalized revenue; open-weight pricing | SEC, primary model/api pricing, qualified market/usage data | no unadjusted multiple transfer |
| Macro | US Treasury yield curve, HY OAS, deal-specific credit spreads | tested Massive Treasury, FRED, bond transaction data | B02 dated per-security ingestion |
| OpenAI derivative sentiment | HIP-3 contract-specific oracle vs mark/funding/OI/depth basis | direct Hyperliquid API, not media summary | isolated sentiment, cannot mark parent NAV |
| Parent economic exposure | SVF2 base OpenAI embedded mark, fund fee waterfall, PBC preferred rights and net attributable stake | SoftBank SOTP and securities filing | B09 #28 net NAV blocked |

### Avoid erroneous source-to-variable mappings

- Revenue numerator: `revenue_recognized_t`, not exit run-rate, bookings, cash funding, supplier RPO or growth target.
- Enterprise value ≠ preferred financing post-money equity mark. `EV = market-equivalent common+preferred economic equity + net debt + minority claims - non-operating assets`, with explicit bridge.
- FCF: `FCFF = EBIT×(1-T)+D&A-capex-ΔNWC`; this formula does **not** treat cash raised as operating profits. For GPU-dependent software, record power, provider contracts, hardware commitments and prepaid credits rather than pretending cash burn belongs to only one counterparty.
- `Net funding need_{t} = max(0, minimum_cash_t - cash_before_financing_t)` with separate issuance timing, discount, dilution, mandatory claims, cash collateral and restricted proceeds. Do not subtract cash from valuation twice.
- Equity/share `IPO_share_value = bridge_equity_value / post-conversion fully diluted count` is unavailable until share rights known. A 2027 exit multiple is a *scenario assumption* until genuine comparable cashflow and pricing disclosures.
- SFTBY NAV: `ΔNAV = new net-SBG-attributable OpenAI value - embedded old net-SBG-attributable OpenAI value - incremental taxes/fees/financing + other dated reconciled changes`. SBG's debt yield is not OpenAI's WACC. No double counting of Vision Fund assets.

## Shifting measurements responsibly

Use different mathematical objects for **research attention** and **company value**:

```text
Research_Weight_i(t) = stage_base_i(t) × regime_modifier_i(t) / Σ_j(stage_base_j × regime_modifier_j)
Selection_Value_i(t) ∝ |ΔEnterpriseValue_i under a plausible input shock|
                        × unknown_materiality_i × source_feasibility_i
Fundamental_Equity_Value_t = DCF_of_company_operating_FCFF_t + net_nonoperating_assets_t
                             − debt_t − preferred_senior_claims_t
```

Research weights are capped/normalized (already in `ipo2027-policy.json`). The *next-data priority* `Selection_Value` is a conceptual target; **do not output a quantitative number until B04 has validated base/shock scenarios and access constraints**, and do not treat it as a probability. Company equity is cash-flow/capital-stack economics, not a weighted sum of qualitative scores.

Maintain two kinds of updates:

- **Calendar-driven**: completed trading sessions for public peers; quarterly issuer/SEC statements; 90-day balance-sheet freshness; explicit monthly adoption sampling. Never autofill missing periods or quote public-company market history as OPENAI trading data.
- **Event-driven**: publicly released S-1; audited revenue restatement; actual SoftBank/OpenAI financing settlement; conditional preferred conversions; change in CUDA/GPU economics; credit spread break; completed Anthropic offering; contract capacity delivered vs announced. An IPO stage progresses **only** on verified filed/priced/listed evidence, not the current date.

TTD must be assigned by **source class** and calculation dependencies: minutes for market marks, one trading day for completed public stock/credit sessions, quarterly filing periodicity for financials; source record remains immutable after expiry but stops qualifying as a *current* input.

### Regime-switch safeguards

A strong one-day market reaction does not identify a persistent causal regime. Candidate regime checks use a trailing same-as-of distribution, repeated independent data, duration and alternative factors:
- credit stress: HY OAS and issue-level bonds; must separate treasury moves from spread; financing delay/capacity effect independently demonstrated;
- competitive price compression: observed effective API pricing *and* net unit margins/retention; benchmark wins not enough;
- IPO pricing: real issuer-underwriter revised offer ranges, filings, institutional orderbook evidence if available; not hypothetical perp notional;
- capability breakthrough: actual post-release revenue per token / contract utilization, not benchmark scores alone.

Store transition provenance, model commit/epoch, source availability and competing explanations. A change in regime reweights *evidence-collection priorities* immediately; changing **fair value** requires a corresponding change in measured economics.

## Next steps by receiver domain

1. B13 existing PR #31: maintain issuer source inventory and contradiction register; this new provider audit remains research-only.
2. B01 #35: actually execute `research/OPENAI/{check.py,ipo2027.py,test_ipo2027.py,resource_audit.py,test_resource_audit.py}` on the PR head and include regression tests in strict CI (the shared store validator does **not** run them).
3. B00 #29: define cross-company valuation class, security rights, as-of/TTD and derivative vs primary round semantics; **B00 #36 queue path stays blocked by PR #25 collision**, do not edit planner from B13.
4. B02 #11: validated SEC/Massive/FRED/Hyperliquid connector data requires **B02-owned runtime**, timestamps, revision journal, entitlement and durable worker; prioritize SEC/public peer and Treasury rather than speculative perps.
5. B03 #12: EDGAR primary issuer/partner events with accession IDs, filing-time vs economic-date distinction; especially public S-1 if released.
6. B04 #30: peer normalization, 5–7-year cashflow, GPU margin/inference curve and security-class-sensitive EV↔equity valuation; sensitivity attribution and model snapshot.
7. B09 #28: SoftBank Vision Fund 2 base-value substitution and funded-debt/FX waterfall.
8. B21: causal claims with counterfactual and negative evidence; B07/B06 after IPO for evaluated predictive calibration and traversal.

**Integration status:** Source research and source-readiness code are candidate B13 assets; no provider was configured as an always-on feed in this worker, no IPO offer is known, no SFTBY NAV calculation is made, and no autonomous repricing is claimed.
