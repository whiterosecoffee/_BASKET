# CROSS_WINDOW: reading TODAY, 72H and 10D together

Vector: the point of having three windows. Each window is built independently from `TODAY.md`, `72H.md` and `10D.md`; this file reads them side by side and produces the scenarios and ladder.

## Inputs
- The three window outputs, each with its own data age and TTD. The oldest TTD governs the cross-window result.

## Procedure
1. Nesting: is TODAY's range inside, at the edge of, or outside the 72H range, and 72H inside 10D? Print the three positions (0 to 1) side by side.
2. Confluence: bands overlapping in two or more windows are merged into one level, with a note listing which windows contribute. Do not add their volumes.
3. Conflict: if regimes differ across windows, report the conflict and which window's edge the latest bar is closest to. Do not average regimes.
4. Transition events: a TODAY break that is a retest of a 72H or 10D band is the highest-information event; flag it first.
5. Shared-bar warning: the windows overlap in bars, so agreement across windows is not independent confirmation. Say it once in the output.
6. Event handling: windows with an event dislocation are reported with and without the event bars; scenarios use the version that excludes the event unless the event is the thesis.
7. Scenarios: base, bull, bear, each with the USD levels that move it and the observable that confirms it. No probabilities.
8. Ladder: if price holds above X then Y, if it breaks X then Z, with invalidation levels taken from the band method. Label every level with its window and method.

## Output
- Nesting line, confluence list, conflict line, transition events, scenarios, ladder, data ages, gaps. Final line: "Next step: <queued action>".

## Failure modes
- Treating three windows as three votes.
- Averaging regimes.
- Ladder levels with no timestamped source or no window label.
- Using levels after the oldest TTD has expired.

## Open parameters
- How close to an edge counts as "at the edge" (v0: within one band width).
- Maximum ladder rungs before the output exceeds one screen.
