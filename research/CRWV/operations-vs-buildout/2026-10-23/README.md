# CRWV — operating margin vs buildout cost (2026-10-23)

Spark B10 · Issue #71 · Machine-readable record: `findings.json` · Arithmetic check: `python3 -I verify.py`

**Data age:** market data through Fri 2026-10-23 close plus 20:21 ET after-hours screenshot; financials are Q2 2026 (reported 2026-08-11). **TTD:** market data expires Mon 2026-10-26 pre-market; financials expire at the Q3 print (date unconfirmed). US markets closed at time of writing.

## Bottom line
Cash operations are profitable (adj. EBITDA margin 59%); buildout cost (depreciation + interest, about 79% of revenue) exceeds EBITDA by about 20 points, giving a net margin of about -24%. Only about 36% of contracted power is active, and implied H2 capex funds little of the 2026 active-power target, so most H2 spend pre-builds 2027+ capacity.

## Q2 2026 per $100 of revenue ($2,575M) — issuer figures, derived percentages
| Layer | % of revenue | $M |
|---|---|---|
| Adj. EBITDA (operations) | +58.6 | 1,510 |
| D&A (buildout, hardware) | -54.1 | 1,393 |
| Net interest (buildout, financing) | -24.9 | 640 |
| Other (stock comp, tax, etc.) | -4.0 | 103 |
| Net loss | -24.3 | 626 |

Interest / adj. EBITDA = 42.4%. Q3 interest is guided to $860-940M, so Q3 adj. EBITDA must reach about $2.1B to hold that ratio.

## Capacity conversion
- Active 1.5 GW vs contracted 3.7 GW (6/30) and 4.2 GW (8/11): 40.5% / 35.7% active. Year-end target of more than 1.85 GW leaves about 2.35 GW contracted but not active.
- Construction in progress $11.9B at 6/30 (from $9.6B); about 300 MW landed in June.
- Capex: H1 about $16.2B; H2 about $20.8B at guidance midpoints (Q3 $11.5-13.5B, Q4 about $8.3B implied) against about +0.35 GW of guided year-end active power (floor).
- Funding: more than $32B secured (period basis unclear) vs FY capex $35-39B; trailing operating cash flow $6.91B is about 19% of the FY midpoint.

## Tape and credit context (third-party reporting)
Closes: 10/12 $80.26; 10/14 $65.78 (-15.5%); 10/16 $61.39; 10/22 $55.60 (-10.1%); 10/23 $54.235 (-2.5%), after-hours $53.95. Down 32.4% over eight sessions. Reported drivers: unsecured bond yields near 15%, 5-year CDS record about 1,195 bp, B+ rating, AI-debt selloff.

## Scenarios (hypotheses, no probabilities assigned)
S1 range about $50-62 while credit leads; S2 breakdown on a close below $53.50; S3 relief on a close above $62 with bond/CDS stabilization.
Invalidation tests: Q3 adj. EBITDA below about $2.1B; EBITDA margin below 56%; year-end active power below 1.85 GW; CIP rising without in-service transfer; exit ARR below $18.5B; new financing priced near 15%.

## Related topics (separate branches)
- Replacement cost, contract rates per MW, depreciation sensitivity: issue #73 / draft PR #74 (`research/CRWV/73-replacement-cost-rates/`).

## Open items
- No management statement of a forward 75% margin found; 74-75% figures are gross margin from 2025 coverage and a third-party model.
- Debt: June 30 totals are reconciled in #68 / PR #69 ($35.068B funded debt + $16.319B operating leases + $0.221B finance leases = $51.608B; different inclusion bases). Still open: October/current balance and the third-party about $42B pro forma estimate (not an issuer figure).
- Q2 gross margin not verified from primary filings. Backlog recognition: the repo's narrative case (engines/narrative/cases/coreweave_2026-10-16.jsonl, record crwv-rpo-frac0) carries 41% of Q2 backlog within 24 months from the 10-Q; not independently checked here, and it supersedes the Q1 36% cited in the findings.

Sources are listed in `findings.json`.
