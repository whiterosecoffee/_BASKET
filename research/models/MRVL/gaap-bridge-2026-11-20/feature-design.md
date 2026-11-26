# Adjusted earnings to GAAP sensitivity

Parent: repository root AGENTS.md and B04 scope in orchestration/sparks.json. This component adds one MRVL instance; it does not duplicate the existing merger model (issue189/PR191).

## Problem and contract
Input: public dated issuer reconciliation, amortization schedule, adjusted EPS/revenue scenarios, diluted common-equivalent shares, excluded cost/tax assumptions and dated price reference.
Output: exact historical net-income inverse reconciliation, Q3 issuer EPS-guidance bridge, conditional standalone earnings/multiples and explicit null verified-forward/combined/exact-calendar outputs.

Method:
1. Historical GAAP NI = adjusted NI - all signed adjustment rows, including the signed tax reconciliation.
2. Q3 EPS bridge uses the issuer's own rounded per-share adjustment rows.
3. Reconstruct scenario adjusted NI = adjusted EPS * reference diluted shares. Pretax proxy = adjusted NI / (1-adjusted tax).
4. Scenario GAAP NI = (pretax proxy - SBC -scheduled amortization -new IPR&D amortization -other excluded charges)*(1-GAAP tax), without assuming tax benefits on a loss.
5. EPS = NI/diluted common-equivalent shares; P/E is null if EPS <=0.
6. Precise calendar EPS requires net-income period substitution and calendar-weighted diluted shares. Annual proration is not an exact conversion.

Ordinary operating R&D/depreciation/interest already included in adjusted earnings are not deducted twice. SBC expense and subsequent share-count growth are distinct. Preferred as-converted economics are assumed inside the reference denominator, not added again.

## Prior work and limitations
Pinned merger admission gates: issue189 commit9727f90125a46fe0966c0f746a891ef2aa4cb536. This addendum contributes earnings-quality evidence, with no replacement spread/traversal/combined model. ARM issue287/PR288 independently reinforces retaining ordinary development costs and signed taxes; no code copied or owner scope assumed.

Source EPS*assumed shares is a reconstructed scenario numerator, not verified consensus net income. Future taxes, discrete items and constituent basis are unknown. Exact calendar2028, post-close purchase accounting and a combined forecast remain blocked. Source validity differs from live market freshness; the dated price is not a current feed.

## Review
Checks: historical Q2/H1 inverse income identities, Q3 guidance identity, independent Decimal arithmetic, adverse compensation/tax/IPR&D and dilution direction, deterministic replay, all unknown outputs remain null. Future validation must use matching-period income and diluted shares. No schema or engine generalization until a second independent consumer requires it.

Next smallest useful action: replace Q3 guidance with December1 actuals and revise the Q4/forward source bundle. Merger owner189 handles combined earnings; FETCH207 owns accepted market refresh. Independent financial review and integration pending.

