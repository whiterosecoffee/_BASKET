# Trading-density presentation models

B06 presentation research on existing issue #144, branch `work/144-october-compression-stress`, draft PR #145. This increment is confined to `research/traversal/october_2026_compression_stress/presentation/**`; the parent README remains the controlling detector/falsification specification. It does not satisfy its original A1–A8 gates or replace #108's canonical engine.

## Purpose and models

Keep the familiar time × USD price path. Overlay participation while retaining dated revisits, recency and nested relativity. Eight alternatives share local source data, backdrop selection and Earlier/Later paging:

1. **Volume Rails:** selected-window allocated-volume profile rendered as horizontal lines; thickness/opacity encode relative concentration. The complete-window profile is retrospective and must not be interpreted as already known at the left edge.
2. **Rolling Ribbons:** equal observation-count slices, volume-weighted 20–80% and 40–60% VWAP envelopes. These are descriptive distributions, not confidence/prediction intervals. A short window can have collapsed envelopes.
3. **Revisit Threads:** consecutive same-band VWAP assignments become sampled visit episodes. Circle size grows with visit volume; dotted connectors are returns, not intervening occupancy or exact boundary crossings. Only the busiest bands are drawn for legibility.
4. **Time–Price Heatmap:** time-slice × price-band cells; intensity encodes allocated shares relative to the largest selected-window cell. Cell colors across different backdrops are not an absolute common volume scale.
5. **Nested Profiles:** full-window, last 60/15 supplied minute bars or last 21/5 supplied daily bars. Each profile is normalized to its own peak to compare distribution shape; widths do not compare absolute volume. Short histories may make profiles identical; labels deliberately say bars, not elapsed minutes/sessions.

6. **Compression / Expansion:** a trailing high/low envelope over the price path. Narrowing and widening refer to normalized range width, independently of whether price rises or falls. The view-specific detail slider selects N supplied bars. Each width is 100×(high−low)/midpoint; compare with the preceding disjoint N-bar window. A warmup of N bars is needed for the envelope, 2N for comparison. The tooltip and readout show signed percentage width change and volume ratio against that prior window. Zero-width/zero-volume denominators are unknown rather than infinite. Both zero widths are unchanged. Source history through the selected end supplies warmup outside the visible left edge; plotted domain includes the visible envelope. This is not a volatility forecast or a fitted breakout signal. A dropped old extreme can narrow the rolling envelope without fresh buying or selling, and changing midpoint can affect normalized width even when USD width is stable. Volume ratios are equal supplied-bar comparisons, not same-clock seasonal RVOL.

7. **Swing Structure — separate:** only confirmed high/low structure, with no trading-price path or EMA overlay in this view. The detail slider is the number of supplied neighbors required on each side of a pivot. Vertices are placed at confirmation time; tooltip includes actual pivot time. This makes structural HH/LH/HL/LL relationships distinct from the close path. Too few pivots is an explicit small-window/long-confirmation limitation; reduce the span. An outside candle's intrabar order remains ambiguous.
8. **Movement / Shares & Turns:** two aligned panels: a quiet actual price path above, signed **net USD movement per 1M shares** below. Fixed nonoverlapping N-bar blocks are anchored at the first supplied source bar; incomplete trailing blocks are omitted. Net movement is last close minus first open, divided by total block shares/1M. This is not gross path travel, signed buying, causal price impact or money inflow. A block endpoint reversal diamond marks a sign switch from the last nonflat completed block. Hollow circles mark larger absolute price velocity in the same direction. Both are timestamped at block completion, not retroactively at a price extreme.

Movement metrics keep **time speed** separate from **movement per volume**: velocity=net USD/N supplied bars; acceleration=(current−previous velocity)/N bars, in USD/bar². Lower volume can increase USD/1M without increasing time speed; only the latter drives the acceleration marker. Negative signed acceleration can mean a downward move speeding up or an upward move slowing down; the readout includes direction and phase. Zero shares yields unknown movement/volume; no infinite score or bridged missing point. Weekends, gaps and missing minutes prevent interpreting supplied-bar units as elapsed market-clock units. Inter-block opening gaps are not part of within-block net movement. A first visible completed block may start before the left edge because global source anchoring is retained; its metadata preserves its true start. These views disable the separate EMA overlay to preserve clarity. Time-axis markers use the source completion-bar label; recognition requires that bar to be completed. Exact first-available/ingested timestamps are not inferred from the label and remain upstream metadata.

## Selectable trend reversals

The view displays **one** trend granularity at a time. A 3–90 supplied-bar slider (default 15) changes smoothing continuously: fewer bars expose finer turns, more bars expose broader shifts. No stacked granularities or simultaneous scale lines. Green is rising and red falling; a constant line weight keeps attention on direction switches. Diamonds mark at most the last six sign reversals in the visible window; the readout gives the selected trend state and latest known reversal time. Hover/touch a diamond for its scale, time and smoothed value.

The selected EMA seeds with the first span closes, then applies alpha=2/(span+1). It is unavailable before that seed. Direction is change versus the preceding EMA, using a 1e-10 flat tolerance. A reversal requires a change between the last nonflat direction and the new nonflat direction; an up→flat→up pause is not a reversal. Points and turns are stamped at the first knowable supplied bar. They are descriptive slope reversals, not guaranteed durable price reversals, signed order flow or calibrated trading signals.

Only observations through the selected backdrop end are used, including prior available warmup bars outside its left edge. Earlier/Later paging never consumes future bars. A single fine-scale turn does not establish a broad trend turn: switch granularity to inspect that relationship. Spans count supplied bars, not certified elapsed minutes or exchange sessions. Clipped offscreen EMA portions do not alter the actual-price domain. The swing helper supplies the separate Swing Structure view; it is not overlaid on the price path. Smoothing defaults are presentation choices, not optimized thresholds. Canonical event recognition and calibration remain separate gates.

## Interpretation and review refinements

Movement / Shares & Turns opens by default. Its question is net displacement per turnover and completed-block direction/speed change. Heatmap supplies where/when participation context; Compression / Expansion supplies range conditions; separate Swing Structure supplies delayed high/low progression. Rails summarize location, Ribbons show concentration migration, Threads distinguish sampled returns, and Nested Profiles compare recent vs broader shape. These alternatives are not simultaneous layers or eight independent confirmations.

Ribbons and Heatmap now use an explicit 3–20 requested-slice selector (default 8), capped at supplied observation count, independent of phone/desktop width. Ribbons use equal observation-count slices; Heatmap uses equal elapsed-axis slices. Changing backdrop recomputes those slices and adaptive price bands; this does not yet freeze time/price boundaries across backdrops. Color/profile normalization remains window-relative. Resize invariance is not cross-window comparability.

The detail label states its actual operation: EMA smoothing span; Range lookback; Pivot neighbors on EACH side (N bars of confirmation delay); Completed movement block (N supplied bars). The density-slice selector is separate from this span. Nonapplicable controls are disabled after qualified data loads.

Reversal vocabulary is separated: EMA slope switch, completed-block direction switch, and confirmed swing high/low structure. None alone establishes a durable reversal. Source completion-bar labels are not exact ingestion/availability timestamps. The EMA latest-turn readout flags turns before the visible backdrop rather than presenting them as visible events.

Remaining review work: fixed reference zones and absolute density scales for cross-backdrop comparison; sampled gross-path travel alongside net movement; genuine zone dwell time; real elapsed-time velocity with gap/session qualification; turn evidence cards and independent browser acceptance. Current volume-at-price remains whole-bar VWAP allocation, not exact traded-at-price volume or participant intentions. No calibrated probability added.

## Open and load

Open `index.html` directly in a modern browser, or serve this directory with an existing local static server. No package installation, paid service or API key is required. There are no network requests. Choose a local JSON file with supplied observations; the source file is read in browser memory and not written, uploaded, persisted to browser storage or copied into the repository. The view starts empty deliberately; no synthetic data is displayed as market history.

```json
{
  "ticker": "SYMBOL",
  "source": "source identity and retained snapshot reference",
  "daily": [],
  "minute": []
}
```

Each observation has numeric `t` (UTC epoch milliseconds), `o`, `h`, `l`, `c`, `v` (shares), and numeric/null `vw`. Daily and minute arrays must be ascending, timestamp-unique, OHLC-consistent, positive-price, nonnegative-volume, and use a consistent adjustment basis. Minute timestamps must align to a minute. At most 10,000 observations per array and a 5 MB file are supported. Duplicate/conflicting or invalid data blocks the view rather than silently sorting or guessing. A missing array is empty; both empty is rejected. This is an unregistered presentation input, not a new canonical schema.

The locally retained `NVDA_Density_Options_Data.json` from the conversation has these daily/minute arrays and can be loaded without committing it. No market bars, credentials, screenshots or account state belong in this subtree. Obtain and qualify source observations through the existing B00/B02 resolver/data plane; this presentation does not bypass or implement it. Missing source metadata and completeness cannot be established by rendering the file.

Backdrop selections are **supplied bar counts**, not calendar guarantees. Minute input must already be the intended single premarket session. The view does not filter mixed sessions, identify holidays, certify coverage or perform split/FX conversion. Source/available/ingested timestamps, entitlement and TTD remain responsibilities of the canonical producer. Every view is historical until a separately accepted runtime supplies observations. The window heading uses America/New_York with DST, USD is the explicit input basis.

## Allocation and quality

Whole-bar volume is assigned to its reported VWAP's price band. This estimates volume at price; it cannot reconstruct within-bar trading, aggressor flow, exact dwell time or investor holdings. Missing/out-of-range VWAP remains in total volume and price path but is excluded from density; the unallocated amount is shown. Fractional provider volume is preserved. No net inflow, support certainty, exact time at price or predictive probability is inferred. Ribbons and profiles exclude the same invalid VWAP bars. Interactive shape normalization and adaptive price bins can change between backdrops; do not call that a frozen-zone migration measure.

## Validation

Run from this folder:

```sh
node --check density.js
node --check controller.js
node presentation.test.cjs
```

The suite uses synthetic values only. It tests input rejection, immutable inputs, paging, pivot confirmation timing, prefix replay, ambiguous candles, allocation conservation and construction of all eight SVG models at 320/736 px across five backdrop sizes. DOM construction is **not a browser layout test**. Browser launch in the author container failed because Chromium process sockets were not permitted; no screenshot or browser-interaction pass is claimed. Independent exact-head browser/domain CI remains pending with B01; generic repository CI is not evidence of this suite unless its logs execute it.

## Retained scope and handoff

Existing parent source/falsification obligations remain open. Reuse #108 for canonical adoption, #148/#152 for data/quality, #98 for independent traversal acceptance, and #265/PR266 for the premarket operator consumer. No polling, source store, trade execution, release, automatic merge or shared workflow change is part of this increment. Selection among models and real source/browser acceptance precede production integration.

Review refinement validation: 45 synthetic checks, including every selectable slice count at 320/736 px, invalid-slice guards, view-specific detail semantics and offscreen-turn readout. The 80-render construction matrix remains separate from the added slice-comparison renders. Actual browser layout/control and independent exact-head CI remain pending.
