# CRWV reconciliation — 2026-11-20

This is a continuation of B10 issue #121 / draft PR #122, on work/121-neocloud-market-research. It does not claim that another chat has accepted the handoff. No parallel finance model, ingestion adapter, classifier or canonical dataset was created.

## Source and ownership reconciliation

| Work | Current verified route | Disposition |
|---|---|---|
| Functional specification | #68 / draft PR #69; current head 6d82bccacaaba9855ef6bd27c64d72eb0514c8c9; original source 29463811e8f77eac9d05b631fcb1c6190bf3f3ff | Linked; read functional-tool-blueprint.md and next-conversation-prompt.md at source pin |
| Finance implementation | #86 / draft PR #87; 7a33a6f49a2740a93310fa1c66a8090c25dd110a; research/CRWV/tool/** | Linked; exclusive owner preserved. Sender replay 39 tests + four scenario demo passed. Fixtures synthetic; finite-fleet runoff, not going-concern fair value |
| Domain acceptance CI | #89 / draft PR #90; f07763d929b383b5bef8927007a2d51ef1fe5460 | Historical failure superseded by successful run40919835438; actual source/tests/demo steps verified. Both PRs remain unmerged; tool absent on current main |
| Collision #91 | Historical ownership hold | Retained as history; no claim to #86 paths |
| Existing market captures | PR122 source 08e718b3ce113d9047f40c97c5cbb7f9f1ce9656 | Linked unchanged; October monthly 19,186 rows plus Nov2/3/4 daily candidates; no fresh canonical backfill |
| Data qualification | #196 / draft PR197 b4dd1843c69e6ac4999808e66cbff3105b9b3d51 | Qualified historical integrity acceptance retained; canonical destination #148 and independent source gate #214 remain separate |
| Nov19 price review | post-earnings-price-review-2026-11-19.json | Retained unchanged; its price is historical, not reused as current |
| New earnings basis audit | eps-basis-reconciliation-2026-11-20.json | Added; primary Q3 bridge and contradictory vendor forward conventions separated |
| November20 user market summary | New EPS audit | Confirmed by freshly retrieved Massive daily summary. Separate snapshot now exposes a precise after-hours trade timestamp; this does not retroactively add a timestamp to the summary endpoint |

## Preserved corrections and unknowns

Demand is not shareholder profit. Connect contracted power to active power, customer acceptance/billable power, recognized revenue, instrument-level funding, earnings/cash, dilution and valuation. Capacity labels are not interchangeable; site-level billable MW remains missing.

Commitments differ from draws and eligible availability. Fixed coupons do not reset to secondary yields; floating exposure depends on benchmark resets and hedges. Keep restricted cash separate from unrestricted parent cash. Each funding source needs limits, dates, availability conditions, fees and dilution. Never plug funding gaps with automatic equity. Show deployment consequences and null dependent valuations where unfunded.

Keep capex, accounting depreciation, physical GPU age, economic earning life, residual value, capitalized/expensed cash interest, principal, SBC and taxes distinct. Principal is not an EPS expense; capex is not expensed immediately in full. NVIDIA residual/trade-in guarantees are unresolved without verified CRWV beneficiary, named assets and actual terms. Preserve earlier valuations and compare revisions at the same target date. Scenario weights remain subjective, not calibrated probabilities.

Q3 management statements — $13.0–13.3B FY2026 revenue, $1.275–1.375B adjusted OI, $37–39B capex, $20–21B December annualized revenue run rate, $1.05–1.15B Q4 interest, expected ~$9B deposits/prepayments over three months, less than $5B incremental parent capital through2027, adjusted profitability during2028 — are guidance/statements, not funded or recognized outcomes. Verify actual receipts, facilities and deployments before model use. Exit ARR is not full-year revenue; backlog is subject to delivery/service conditions. No contract is counted twice across spending, backlog and revenue.

## Earnings conclusion

Q3 GAAP net loss of $709M becomes adjusted loss of $529M through +$160M SBC, +$12M acquired-intangible amortization, −$11M other adjustments and +$19M tax adjustment. That actual $180M gap cannot establish future-year exclusions. Tenet labels forecasts Street basis and derives displayed shares from NI/EPS; MarketScreener panels do not reconcile to each other and imply a2028 loss. Therefore $1.51 EPS and 26.2× at $39.51 remain conditional Street arithmetic. A verified2028 GAAP P/E and fair-value target remain unavailable.

## Market traversal handoff retained

Use existing #70, including https://github.com/whiterosecoffee/_BASKET/issues/70#issuecomment-6470943511. Compare trailing5/15-minute windows at one cutoff against their preceding nonoverlapping equal windows, separately for premarket/RTH/after-hours. Report upward/downward close movement per $10M executed notional, net displacement, turnover, local VWAP and rebound participation, raw denominators/sampling/source/cutoff/freshness. Synchronize QQQ/NVDA/named peers. Specify bands, hysteresis/minimum separation, failed reclaims, higher/lower lows and acceptance rules.

Minute bars do not show aggressor side, replenishment, exact volume-at-price or intrabar ordering. Options OI, resting orders and executed stock volume remain separate. Screenshots are dated evidence, not proof of current gamma or dealer positions. Cycling requires predeclared bands/first passage/censoring/ambiguous bars/held-out validation/spread/slippage/fees before probabilities or an edge.

Proposed states remain unimplemented: markdown, downside test, stabilization, absorption candidate, reclaim attempt, accepted reclaim, upward expansion, rejection/distribution candidate, balanced chop, insufficient data. One primary state plus range/direction/participation/relative-strength/liquidity/event modifiers; each needs entry, persistence and invalidation. Absorption/distribution are hypotheses.

## Next action

Owner #86 should reconcile source-defined2027–2028 adjustment definitions and weighted diluted shares, then add actual receipt/draw/commissioning evidence to its existing model. Do not substitute cross-provider ratios for an earnings bridge. No receiver or Dot acknowledgment has been observed.
