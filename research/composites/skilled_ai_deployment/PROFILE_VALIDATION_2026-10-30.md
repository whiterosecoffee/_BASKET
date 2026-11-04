# B17 profile-structure audit — 2026-10-30

Scope: `profiles/*.json`, 24 independently fetched GitHub files, branch `work/118-skilled-ai-deployment-basket`. This is a connector-side JSON parse and presence audit, **not** a B01 independent CI suite and not evidence of financial number correctness.

## Results
- 24 of 24 profile JSONs fetched and parsed as valid JSON (two batches of 12).
- 24 of 24 contain ticker, earnings object and partnerships object.
- All 24 passed targeted check: a non-null 2027 forward P/E must not exist with null 2027 EPS.
- Nine initially failed venue precision check (`USA` is a country, not a listing venue). Corrected to: `PATH:NYSE`, `CSCO:NASDAQ`, `QCOM:NASDAQ`, `CACI:NYSE`, `INOD:NASDAQ`, `DELL:NYSE`, `HPE:NYSE`, `DXC:NYSE`, `DBRG:NYSE`. Exact listing venue still requires authoritative securities-master confirmation; corrections are provisional.
- The initial 24 ticker set is: GLOB, EPAM, PATH, CSCO, QCOM, G, EXLS, CTSH, CINT, GDYN, DAVA, CACI, INOD, DELL, HPE, IBM, DXC, PLTR, ACN, DBRG, GIB, KD, INFY, WIT. Unique ticker codes: 24.
- No 2027/2028 analyst consensus figures were guessed or inserted. Incomplete EPS, P/E, provider observed/available times and partner-attributed sales stay null.

## Open gates
1. B01 independent validation on PR exact head and fail-closed contract fixtures. Check all 24 profiles, consistent fiscal period, currency/FX, stale observation semantics, ticker venue key, partner evidence, source availability and cross-file parity.
2. B17 confirm listing symbols with an authoritative security master, then reconcile basket candidates vs screenshot-only adjacent hardware/infrastructure and fill dated individual issuer source evidence. Screenshot prices are not verified closes.
3. B00 register canonical basket object and referenced profile contract via #119.
4. Financial profiles need dated primary EPS/guidance, current 2027–2028 estimates, reconciliation to GAAP and cash flow before valuation scores.
5. Exact-head workflow outcome must be checked after these amendments; earlier green workflow applies to earlier head only.

## Acceptance
Research-only PR may be accepted with explicit unknowns; do not claim all profiles complete or production data correctness. No main merge authorized.
