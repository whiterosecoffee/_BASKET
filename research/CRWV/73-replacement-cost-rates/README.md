# CRWV — replacement cost, contract rates per MW, depreciation sensitivity

Spark B10 · Issue #73 · Record: `findings.json` · Check: `python3 -I verify.py` · Split from PR #72 (topic: operating margin vs buildout, issue #71).

**Data age:** market cap from the 2026-10-23 close (user screenshot); debt, cash and construction in progress at 2026-06-30; rate and cost sources dated 2026-07-28 to 2026-10-08. **TTD:** market cap expires Mon 2026-10-26 pre-market; contract rates expire at the Q3 2026 print. Mixed dates are flagged in the file.

**Correction:** the $30-50M/MW figures are build-cost estimates (FT/Benzinga about $50M; Gainam $30-40M all-in), not contract prices; SpaceX (SPCX) contracts carry no MW figure.

- **Replacement cost:** 1.5 GW active x $30-50M = $45-75B. EV net of construction in progress per active MW: $30.7M (debt only), $35.4M (third-party pro forma), $41.8M (incl. leases). Lease-inclusive is the comparable row: priced about at replacement cost, not clearly below.
- **Debt basis:** June 30 reconciled in #68 / PR #69: $35.068B funded debt + $16.319B operating leases + $0.221B finance leases = $51.608B. The about $42B pro forma is a third-party estimate, not an issuer balance.
- **Contract rates:** new Q3 contracts about $40M per MW annualized, 3-6 month terms (company release 9/17). No pre-increase rate disclosed; if the reported 25% (July) plus about 10% increases apply, implied prior rate about $29M/MW (derived, unverified). Blended exit ARR is about $10M/MW (mixes ramp and cost vintages). H100 list price is about $42M/MW equivalent at full utilization (assumes 10.2 kW per node).
- **Payback (gross):** 1.3-2.1 years at $40M/MW vs 4.8-8.5 years at the blended rate.
- **Depreciation:** a 6 to 8 year life cuts D&A about 25% (upper bound about $348M per quarter) but is non-cash; interest stays about 42% of adj. EBITDA. Years 6-10 are uncontracted; the longer-life thesis needs abundant power.

**Open:** CoreWeave stated GPU useful life and D&A split by asset class; pre-increase $/MW rate; whether the price increases apply to existing contracts.

Sources are listed in `findings.json`.
