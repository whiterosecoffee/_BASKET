# Earnings and funding evidence qualification

Consumer: existing CRWV #86 tool owner and the main CRWV analysis session.
Reuse decision: retain #86 monthly engine; add only a disjoint B10 source-audit
script because current provider numbers cannot safely populate its real inputs.
Prior art: #69 blueprint, #87 model, #90 pinned-source acceptance, and merged
architecture/COMPONENT_QUICKSTART.md. Shared boundary adoption remains owner work;
this local contract does not claim qualified_refs_v1 conformance.

Input: evidence/snapshot.json, USD millions except price/EPS; source IDs, period
ends, availability and observed timestamps, separate GAAP/adjusted earnings,
carrying debt/principal/leases/cash, and provider-specific forecast rows.
Entry: evaluate(snapshot, timezone-aware as_of). Pure arithmetic; no network,
mutation, subprocess or scheduling. CLI reads one local file and writes JSON/text.
Output: reconciled historical bridges, source states, per-provider qualifications,
diagnostic ratios separately from verified GAAP P/E, funding-input completeness,
source/config identity via canonical input SHA256 and method version.

Formulas:
- GAAP net income = operating income - net interest + other income - tax.
- Adjusted net income = GAAP net income + signed disclosed reconciliation items.
- EPS = same-period income / same-period weighted shares (millions cancel).
- Principal = carrying debt + unamortized discount/issuance costs.
- Net debt with finance leases = carrying debt + finance leases - unrestricted
  cash - marketable securities. Restricted cash is never freely available cash.
- Ending total cash = opening total cash + CFO + CFI + CFF.
- Pretax residual = reported EBT - (reported EBIT - reported interest).
  An unexplained residual is missing evidence, not permission to replace EBT.

Exceptions: amounts are rounded filings; EPS tolerance 0.01, matching provider
income/share EPS tolerance 0.02. NaN/infinite/boolean/missing numeric values fail.
Timezone-free dates fail. Source availability after cutoff suppresses dependent
values. Unknown first publication remains unknown; issuer source available_at is
the conservative retrieval bound, not a fabricated Nov10 timestamp. Third-party
forecasts lack an auditable point-in-time vintage and stay unqualified.

Funding completeness requires actual current opening cash, monthly uses, draw
conditions, deposit receipts, restriction release terms and covenant headroom.
Even complete fields only return ready_for_owner_evaluation, never fully_funded.
The monthly calculation, including an actual gap, remains #86's responsibility.

The $39.51/556.126M price-share pair is an earlier conversation reference. Its EV
combines November20 equity with September30 balance data and is always labelled
mixed-date, not current. No forward EV is presented using frozen debt as a fact.

Planned alternatives: a reconciled GAAP forecast adapter, a separately reconciled
adjusted forecast adapter and the owner monthly funding adapter. Their additions
require exact fiscal periods, denominator, signed adjustments, receipt/draw terms
and receiving-owner acceptance. They are not implemented here.

Coverage limits: numeric bridge agreement does not verify a provider, legal debt
terms, ongoing covenant compliance, complete GAAP forecasts or economic GPU life.
Tests use source-derived fixture arithmetic and synthetic negative/positive gate
cases. No probabilities, perpetual fair value or live runtime is produced.
