# DIVERGENCE_OVERLAY: TARGET versus benchmarks over the same three windows

Vector: is TARGET's traversal its own, or the market's. Secondary to the range work; it never changes a band, only how it is read.

## Inputs
- Bars for QQQ, NVDA, IBM, HYG, IEF and USO for the same windows and sessions as TARGET (B02 store or the entitled Massive connector). TTD matches the freshest TARGET window.
- Prior-window data for betas and standardization. Only information available at each bar may be used; no lookahead.

## Procedure
1. Align timestamps and sessions exactly. Where a benchmark trades on a different calendar (HYG and IEF can have different early closes), align on the common bars and say what was dropped.
2. For each benchmark and each window compute: benchmark return, TARGET return, and the difference.
3. Standardize the difference against the trailing 60 sessions of the same measure, using prior-window betas only. Report raw and standardized values side by side.
4. Read each benchmark for what it represents:
   - QQQ: broad growth and market direction.
   - NVDA: AI compute and supplier sentiment, not a valuation peer.
   - IBM: legacy enterprise and hybrid peer.
   - HYG and IEF: credit and rates. Falling yields with widening credit can mean stress rather than relief.
   - USO: futures-based energy proxy; separate verified supply effects from headlines.
5. A missing benchmark suppresses its comparison. Do not silently reweight.
6. The tracker's macro baseline weights (0.40 credit, 0.20 rates, 0.25 energy and inflation, 0.15 execution) are a heuristic, not fitted sensitivities. Do not reuse them as betas.

## Output
- One line per present benchmark per window: window return difference, standardized value, direction. Gaps listed. One line on whether the traversal looks idiosyncratic or market-driven, labeled as a reading, not a finding.

## Failure modes
- Lookahead in beta or standardization.
- A short, illiquid window producing a large standardized value from tiny variance.
- Calling a divergence a signal without checking the event calendar.

## Open parameters
- Trailing window length for standardization (v0: 60 sessions).
- Minimum number of common bars for a window comparison.
