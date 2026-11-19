# 06 Thesis, invalidation and decision ladder

Vector: turn the ranked evidence into a decision structure. Consumes vectors 01 to 05 and, optionally, Range_Traversal reference levels.

## Inputs
- Rank and stability from `03_UPSIDE_SCORE.md`, gap from `04_REVERSE_CHECK.md`, tilt and flip factors from `05_FACTOR_CHECKLIST.md`.
- Optional: nearest band edges and invalidation levels from `research/ORCL/Range_Traversal/CROSS_WINDOW.md`.
- Date of the next report and the options-implied move.

## Method
1. Expand first: write the clearest, strongest bull case for the top-ranked name, in full, without hedging.
2. Contract second: list invalidation conditions as measurable thresholds with a source, a date or event, and the factor they belong to. Do not lead with challenges or split hairs over wording.
3. Test at least three valid framings and score each before recommending one:
   - Re-rating: discount closes toward the peer median or own history.
   - Earnings growth: NTM EPS growth and revisions carry the stock.
   - Catalyst-driven: the next print and guidance move it, regardless of multiple.
4. Ranked scenarios: base, bull, bear. State what moves each and the observable that would confirm it. Probabilities only if computed from stated inputs with the math shown; otherwise omit.
5. Decision ladder: if X then Y, with levels in USD and the invalidation trigger. If range levels are available, use them as reference points and label them as such.
6. Ghost nodes: valid but not-next items, one line each.

## Output
- Bottom line first. Then bull case, invalidation list, framings with scores, scenarios, ladder, ghost nodes.
- Assumptions, gaps, data ages and TTDs, uplift self-score.
- Final line: "Next step: <queued action>".

## Failure modes
- Recommending from one framing only.
- Invalidation phrased as a mood rather than a threshold.
- A ladder with levels that have no timestamped source.
- Presenting the recommendation as advice: this is analysis, not a trade instruction.

## Open parameters
- How many ladder rungs before the output exceeds one screen.
- Whether the three framings should be re-chosen per TARGET.
