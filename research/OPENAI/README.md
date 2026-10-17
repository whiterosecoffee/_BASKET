# OpenAI pre-IPO research — B13 (2026-10-17)

**Canonical entity**: `tickers/OPENAI/entity.json`, `entity@1`. `OPENAI` is an **internal issuer identifier**, **not** a listed ticker and not a user-tradable price series. `tickers/OPENAI/history.jsonl` remains B02-owned and must **never** contain manufactured OHLCV for the private issuer.

**Worker scope:** #26 `work/26-openai-preipo-valuation-sftby`. Owned writes: `tickers/OPENAI/entity.json` and `research/OPENAI/**`. Shared architecture contracts, market history, events, relationships and parent NAV remain read-only. Core project version is NOT bumped.

## Contents

- `valuation-register.json`: normalized **source-classed** dated primary financing benchmarks, channel revenue proxies, secondary commentary and explicit unknowns. Same financing round $730B pre-money + $122B committed capital = $852B post-money, not three equity marks.
- `assumption-register.json`: disputed/falsified/untestable claims, opposing interpretations, required measurements and future triggers. Narrative claims don't become observations because they are repeated.
- `sftby-interface.json`: precise economic graph of SBG → SVF2 → OpenAI preferred shares; canonical de-dup rules, requirements for net SBG entitlement, LTV and USD parent look-through scenarios. **No reported current NAV**.
- `check.py`: local standard-library source integrity and conditional scenario checker. **Not** a production B04 valuation engine or B09 NAV engine.

Run offline:
```bash
python research/OPENAI/check.py --validate
python research/OPENAI/check.py --valuation-usd-b 852 --stake-fraction 0.13 --move-pct -4 --as-of 2026-10-17
```

The research records have **date precision**. `available_on` means the source was public that calendar day; it is not an invented 00:00 UTC publication time. `ingested_at_utc: null` explicitly marks missing independently measured ingestion. For point-in-time intraday replay, data must be re-ingested by B02 with verified timestamps and revisions. A June period end is not the article's October as-of date. All values are USD-first; foreign parent NAV requires date-matched FX for any conversion.

## Valuation methodological ladder

| Class | What it measures | Requirements | Current eligible use |
|---|---|---|---|
| Financing PRE-money | Equity value before the round's new financing | legal entity, price, security rights, date | historical benchmark |
| Financing POST-money | Equity value immediately after priced round, with commitments and settlement separately tracked | cash committed vs funded, dilution, preferred terms | historical benchmark, **not current fair-value tick** |
| Actual secondary transaction | Real investor sale/purchase | transferred class, price, size, close, restrictions | none confirmed in this dataset |
| Fundamental enterprise value | Operating enterprise PV based on margins/cash flow | normalized financials, net debt/cash, contractual commitments, discount rate and dilution | blocked; B04 model required |
| Third-party revenue proxy | Period-specific operating information | GAAP alignment; direct/reseller gross-vs-net; reported/recognized; source/period | provisional comparison only |
| Hyperliquid HIP-3 perp implied capitalization | Speculative derivative benchmark | exact contract/oracle, denomination, funding/mark, venue liquidity, notional OI, timestamps | sentiment only, **never company equity NAV** |
| IPO indication | Indication of future offering price | filed S-1, security/conversion, banker underwriting and issuer pricing | unavailable; no announced ticker assumed |

### Mandatory split: equity value vs enterprise value

`EV = equity value + net debt + other claims - non-operating cash/assets` (exact bridge must list minority interest, preferred rights, leases and double-counting assumptions). The $852B fundraising post-money is **equity funding valuation**, *not* enterprise value and not a per-share price. Do not compare it to operating EBITDA multiples unless the bridge is explicitly established. No synthetic IPO allocation or common-share count is assumed.

### Run-rate and per-unit economics

Reuters on Oct 8 reported **almost $50B annualized September 2026 revenue** and a previous approach to $70B, with important cloud-channel gross/net scope differences (OpenAI does not include sales through selected cloud partners in the cited comparison). Neither is audited full-year revenue. A mechanical `852/50 = 17.04×` is a **cross-date, source-methodology-dependent post-money equity/run-rate proxy**, not EV/sales and not a target multiple.

Missing data that block fair-value accuracy:

1. Actual GAAP quarterly sales, direct/indirect channel gross vs net, by inference/training, application and enterprise; annualized one-month estimates are not retained revenue.
2. Token economics: price per delivered workload, utilization, inference marginal cost, training amortization, GPU useful life/refresh credits, model efficiency and gross margins.
3. Contract ledger by counterparty: signed/announced/funded; compute MW/GPU/term, minimum spend, prepayments, SLAs, cancellation rights, capacity deliveries, discounts and price escalation.
4. Financing, unrestricted cash vs subscription/prepaid restricted funds, leases, capex, debt maturities, available borrowing, collateral and special-purpose vehicles.
5. Fully diluted security class cap table, Foundation control/warrants, preferred liquidation/participation protections, IPO conversions and future dilution.
6. As-of market benchmarks: actual transacted secondaries (if available), independently reconstructed derivative oracle, liquidity depth and basis, source timestamp and TTD.

## SFTBY integration: **replace** embedded SVF2 value; do not add a new line

Official SoftBank 2026-06-30 reporting places **SVF2 as a constituent of existing NAV**; its disclosed definition is SBG's share of SVF2 NAV, etc. OpenAI stakes via SVF2 must already be represented to an extent within that component. As a result:

```text
ΔSFTBY_reconciled_NAV_USD =
    Δ(net_SBG_attributable_OpenAI_preferred_fair_value_USD)
  + Δ(other_parent_net_assets_USD) - Δ(adjusted_net_debt_USD)
  - incremental_fees_taxes_financing_adjustments_USD
```

The original embedded OpenAI fund mark must be **removed/replaced**, not added twice; the rest of SVF2 must remain. `0.13 × $1.5T = $195B` describes only an illustrative **gross** stake mark at a speculative issuer-wide equity valuation; it is NOT verified SBG parent net NAV, and no specific SFTBY equity or ADR price delta can be derived. `-4% × $195B = -$7.8B` is a hypothetical gross stake sensitivity, not a realized loss.

Two crossed dates (March round and October approximate ownership) never imply a matched-date market cap. Future waterfall, profit-sharing, FX and margin-financing data must reconcile to official SBG June 30 base and new periods. OpenAI's own USD valuation should not be mechanically FX-adjusted just because SFTBY reports in JPY; translate SBG's USD financing liabilities, JPY domestic costs/assets, USD holdings and parent equity using matched dates and exposure denomination. Keep 9984.T and SFTBY ADR mapping in B09.

## Cross-domain integration contracts (proposed, not implemented)

- **B00** versioned shared data contracts: `private_security`, `round_event`, `issuer_value_reference`, `market_proxy`, `net_investor_attributable_value`, plus immutable provenance/TTD/currency standards.
- **B03**: actual OpenAI financing/IPO/compute-contract lifecycle in `tickers/OPENAI/events.json`; immutable effective/available/ingested dates. Prevent repeated $730/$852/$122 triple counting.
- **B05**: verified SFTBY → SVF2 → OpenAI economic edges plus CRWV capacity flows, contracts vs ownership; typed confidence and dated source.
- **B02**: Entropy IO `io:OAI` or equivalent **derivative instrument** distinct from `OPENAI` private equity. Store separately with contract oracle, mark, funding, OI and venue-quality provenance; never append to issuer OHLCV.
- **B04**: company revenue/FCF/valuation models with explicit cash/EV waterfall and sensitivity, model commit/version and snapshot IDs.
- **B09**: SFTBY look-through fund NAV (net attributable after fees/finance) and ADR/FX/LTV with matching valuation dates; scenario view separate from reported NAV.
- **B21**: hypothesis and causal tests (CoreWeave credit → OpenAI perp repricing) with counterfactual alternatives, event-time controls and durable falsifiers.
- **B01**: wire strict validation/integration after owning owners publish accepted contracts.

### Sources (primary first)

1. https://openai.com/our-structure/ — 2025 Foundation/PBC recapitalization and historic 26%/warrant.
2. https://openai.com/index/scaling-ai-for-everyone/ — 2026-02-27 funding commitments and compute/distribution partnerships.
3. https://openai.com/index/accelerating-the-next-phase-ai/ — 2026-03-31 $122B committed, $852B post-money.
4. https://group.softbank/en/news/press/20260227 — 2026-02-27 $730B pre-money preferred-share IPO conversion terms.
5. https://group.softbank/en/news/press/20261001 — 2026-10-01 completed $10B third tranche, $64.6B cumulative, approximately 13% stake via SVF2.
6. https://group.softbank/en/ir/stock/sotp — 2026-06-30 SBG NAV definition and SVF2 double-counting controls.
7. https://www.reuters.com/business/openais-annualized-revenue-20-billion-less-than-previously-signaled-ft-reports-2026-10-08/ — dated third-party operating revenue methodology.
8. https://tradeinzone.in/heres-how-the-coreweave-sell-off-is-affecting-openai-vs-anthropic-valuations/ — syndicated CNBC derivative sentiment narrative, NOT primary exchange market tape.
9. https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-3-builder-deployed-perpetuals — HIP-3 mechanics, not verification of any individual market's oracle.

**Classification:** B13 component research-only; not a production live input, not actual issuer/fund mark-to-market and not integration/release evidence.
