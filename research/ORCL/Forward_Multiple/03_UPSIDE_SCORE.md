# 03 Upside score and next-quarter setup

Vector: which company has the highest potential for growth from current multiples and forward earnings. Produces the ranking, and tests whether the ranking survives different weightings.

## Inputs
- Blended multiples and gaps from `02_WEIGHTED_MULTIPLE.md`.
- Estimate revisions over 30 and 90 days, consensus EPS and revenue for next quarter, report date (Quartr). TTD: until the next revision or print.
- History of the last eight quarters: beat or miss, guidance versus outcome, post-print price move (B03 events, Quartr, B02 history).
- Options-implied move for the next print (entitled source; flag if unavailable).
- Balance sheet and capex (B04 or filings).

## Method
Total score 0-100 per company, built from four components, each min-max normalized across the peer set so the math is visible:
1. Re-rating gap (default 40%): distance from the blended multiple down to the lower of weighted peer median or own-history blend, adjusted for growth. Larger discount scores higher.
2. NTM EPS growth, revision-adjusted (default 30%): consensus growth, scaled by 30-day and 90-day estimate trend.
3. Next-quarter setup (default 20%): consensus versus whisper where a timestamped source exists, beat history, guidance record, implied move versus historical post-print move, and days to the report.
4. Risk haircut (default 10%, subtracted): net debt to EBITDA, capex to revenue, financing dependence.

Sensitivity (mandatory, tests multiple options):
- Weight set A: base 40 / 30 / 20 / 10.
- Weight set B: growth-heavy 25 / 45 / 20 / 10.
- Weight set C: value-heavy 55 / 20 / 15 / 10.
- Report the rank under each. If the winner changes, say so first and name the component that flipped it.

## Output
- Per company: four component scores, total, rank under A, B, C, and the stability verdict (stable, conditional, unstable).
- Next-quarter lens per company: report date, consensus EPS and revenue, revision direction, implied move, historical move range.
- Data ages and TTDs.

## Failure modes
- Whisper numbers without a source: label as unverified or omit.
- Score read as a return forecast: it is a ranking, not a probability or a price target.
- Double counting: qualitative factors in `05_FACTOR_CHECKLIST.md` never enter this score.

## Open parameters
- Component weights and the 0-100 scaling.
- Growth adjustment form for the re-rating gap.
- Which months of beat history count as one regime.
