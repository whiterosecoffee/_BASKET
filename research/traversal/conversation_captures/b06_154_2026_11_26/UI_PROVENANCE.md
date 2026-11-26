# Range UI provenance and reuse contract

## Verified answer
The “nice visual UI components” for comparing price ranges are a strong match to **PR145**, not PR160. B06 #144 / work/144-october-compression-stress at head feaff2a6a72c09a36f425d309bcb8859c971aab4 contains the offline HTML/JavaScript presentation. PR160's changed-file inventory contains Markdown research and Python calculations/tests but no HTML/JS UI. The exact original in-chat rendered widget identity cannot be proven without a screenshot or export.

## Source paths at exact inspected PR145 head
- research/traversal/october_2026_compression_stress/presentation/index.html
- presentation/controller.js
- presentation/density.js
- presentation/zones.js
- presentation/context.js
- presentation/README.md
- presentation/MATRIX_DESIGN.md
- presentation/context.test.cjs
- presentation/presentation.test.cjs
- presentation/zones.test.cjs

Open source: https://github.com/whiterosecoffee/_BASKET/tree/work/144-october-compression-stress/research/traversal/october_2026_compression_stress/presentation

## Eight implemented selectable views
1. Volume Rails: horizontal traded-concentration lines by price. Selected-window totals do not exist at the start of that window.
2. Rolling Ribbons: observation-count time slices with volume-weighted inner/outer distribution envelopes; not confidence intervals.
3. Revisit Threads: sampled consecutive visits to a price band and revisits over time; not precise executed path/dwell.
4. Time–Price Heatmap: allocation by supplied time slice and price bin, normalized per selected window.
5. Nested Profiles: full and trailing 60/15 minute bars or 21/5 daily bars; shapes independently peak-normalized, so widths are not absolute share comparisons.
6. Compression / Expansion: range-width evolution against earlier disjoint windows, normalized by midpoint; not a fitted direction forecast.
7. Swing Structure: confirmed higher/lower highs and lows, with recognition time separated from pivot time; ambiguous outside bars preserved.
8. Movement / Shares & Turns: price path plus signed net USD movement per million shares, time speed and completed block changes; not signed order flow or causal price impact.

## Controls and matrices
The actual HTML offers Premarket, 5/21/63/252-session backdrops, Earlier/Later paging, smoothing/granularity slider, optional EMA slope turns and adjustable density slices. Its analysis matrix selector includes implemented **Zone Participation** (fixed USD bands, shares/samples/time-block percentages, unallocated totals) and **Nested Context** (short vs parent horizon comparisons). **Turn Episodes** remains a design proposal in MATRIX_DESIGN.md; do not report it implemented.

## Distinctions this future work must preserve
- Level highlighting != evidence of defended institutional support.
- Bar-VWAP allocated shares != exact time-at-price, signed buying or flow.
- A fixed price-bin basis and denominators are necessary for comparable matrices.
- Overlapping nested horizons are not additive, and individually normalized profiles cannot compare absolute volumes.
- Trend confirmation/turn labels must be dated when observable, not when the hidden future-extreme occurred.
- Intraday missingness, source availability, day-vs-minute and volume unit basis must remain visible.
- Same underlying bar evidence may appear in several views; that is presentation variation, not independent corroboration.

## Reuse recommendation
**Keep PR145 as the sole UI implementation owner.** Link exact source and contracts from any historical-state or valuation consumer. If B06 #154 moving-average features are displayed alongside PR145 range UI, B00 must accept the state contract and B02 must qualify the shared timestamp/source; no UI rewrites from this archive.

## What remains unverified
No demonstrated deployed website, actual live Massive feed or source-qualified end-to-end test for the presentation. No screenshot or serialized ChatGPT widget from this conversation. The remembered “nice” look may refer to an in-chat visualization rather than this offline repo HTML; source links establish the closest concrete implementation, not visual identity.