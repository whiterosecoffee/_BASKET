# 04 Reverse check: what the price already assumes

Vector: invert the multiple. Instead of asking what a company is worth, ask what growth and margin the current price requires, then compare that to consensus. Separates "cheap on a multiple" from "cheap versus what is expected".

## Inputs
- Price, EV and the blended multiple from `02_WEIGHTED_MULTIPLE.md`.
- Consensus NTM and FY2 growth and margins (Quartr). TTD: until the next revision.
- Weighted peer median multiples and growth from vectors 01 and 02.

## Method
1. Implied growth at peer multiple: the NTM EPS growth at which TARGET's PEG would equal the weighted peer median PEG at TARGET's current price.
2. Implied margin: the operating or EBITDA margin that justifies TARGET's EV / sales at the peer median EV / EBITDA.
3. Compare each implied figure to consensus. State the gap as a number and its direction: price assumes more than consensus (demanding), about equal (priced in), or less (room).
4. Sensitivity: show how the implied figures move under the three weight sets in vector 03.
5. Do not convert the gap into a probability. It is a requirement, not a forecast.

## Output
- Implied growth, implied margin, consensus, gap with direction, data ages.

## Failure modes
- Treating consensus as truth: label it as the market's own expectation.
- Ignoring capex: for ORCL and CRWV, margin implied on EBITDA can hide cash conversion; cross-check against vector 05's capex and FCF factor.

## Open parameters
- Which peer multiple anchors the margin inversion (median versus single closest peer).
- Horizon for implied growth (NTM only versus two-year).
