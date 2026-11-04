# TODAY: the current regular session

Vector: where TARGET is inside the live or just-finished session, and what the session has already shown. Method: `BAND_METHOD.md`.

## Bar set
- 5-minute regular-session bars from the open to the latest bar. Partial while the session is open; full sessions have 78 bars. On a half-day report the actual bar count.
- Pre-market and after-hours are a separate set, shown only as context.
- TTD: 300 s while open. After the close the session is frozen as historical truth until the next first bar.

## Session-specific measures (in addition to the shared method)
1. Session phase: pre-market, open, mid-session, late session, closed. State it first.
2. Gap: open versus prior daily close, and whether it has filled, partly filled or extended.
3. Opening range: high and low of the first six five-minute bars (30 minutes, a v0 parameter). Report whether the latest bar is above, inside or below it. An opening-range edge is not a support band until it earns distinct touches.
4. Session VWAP: the bar-aggregate VWAP, labeled as such, and the latest close relative to it.
5. Carried-in levels: top bands from `72H.md` and `10D.md` that fall inside today's range or within one band width of it, with the touch count today.
6. Time of day: where the touches and the high and low of the session occurred (opening hour, midday, late), since the same band has different meaning at different times.

## Output (three lines)
- Range, position, gap status, opening-range status.
- Top band today with dollar-volume method and carried-in level if any.
- Regime for the session (often unknown early; say so).

## Window-specific tests
- Opening-range floor versus repeated support.
- Partial session: bands flagged provisional, not final.
- Gap-and-go versus gap-fill.
- Stale latest bar: NON-ACTIONABLE.

## Open parameters
- Opening-range length (30 minutes).
- Minimum bars before a session regime may be anything other than unknown.
