# 02 Weighted forward multiple

Vector: a single comparable blended multiple per company, on a common NTM basis, versus the weighted peer median and each company's own history.

## Inputs
- Peer list and weights from `01_PEER_SET.md`.
- Live price, diluted shares, debt, leases, cash, minority interest, preferred (B02 and Quartr). TTD: prices 300 s in session; balance sheet until next filing.
- Consensus FY1 and FY2 for EPS, EBITDA, revenue, FCF (Quartr; web fallback). TTD: until the next revision or print.
- Each company's 5-year history of the same multiples where the store has it. Missing history is a gap.

## Method
1. Calendarize to NTM. NTM = (months left in FY1 / 12) x FY1 + (1 - months left in FY1 / 12) x FY2. Fiscal years differ across the set (ORCL, MSFT and others do not share a year end), so every company is converted to the same as-of date before comparison.
2. Enterprise value = market cap on diluted shares + debt + lease obligations + minority + preferred - cash. State whether leases are included and keep it identical across companies.
3. Default blend:
   - NTM P/E 35%
   - EV / NTM EBITDA 20%
   - EV / NTM sales divided by NTM revenue growth 15%
   - PEG on NTM EPS growth 15%
   - EV / NTM FCF 15%
4. FCF rule: if NTM FCF is negative or capex-distorted (ORCL, CRWV), move the FCF weight to EV / NTM EBITDA and flag it. Do not drop the company.
5. Earnings basis: show non-GAAP consensus P/E and, where the store has it, the GAAP figure beside it. Flag where stock-based compensation or acquisition amortization creates a large gap.
6. Peer reference = weighted median using the vector 01 weights. Also show the weighted mean; if they differ by more than a stated tolerance, flag skew from one name.
7. Positioning: each company's blended multiple versus the weighted peer median (discount or premium in percent) and versus its own 5-year average (percentile).
8. Overlay names (CRWV) are shown beside the table of results and excluded from the median.

## Output (narrow list per company)
- Blended multiple, five component multiples, premium or discount versus peers, percentile versus own history, which weights were reallocated and why, data ages.

## Failure modes
- Mixing fiscal years without calendarizing.
- Treating a negative-FCF company's FCF multiple as meaningful.
- Using trailing figures labeled as forward.
- Dropping the overlay's caveat: its multiple is shown, not averaged in.

## Open parameters
- Blend weights are uncalibrated and are tested for sensitivity in vector 03.
- Lease treatment in EV.
- Tolerance for weighted mean versus median skew.
