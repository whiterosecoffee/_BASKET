# Trading-density presentation models

B06 presentation research on existing issue #144, branch `work/144-october-compression-stress`, draft PR #145. This increment is confined to `research/traversal/october_2026_compression_stress/presentation/**`; the parent README remains the controlling detector/falsification specification. It does not satisfy its original A1–A8 gates or replace #108's canonical engine.

## Purpose and models

Keep the familiar time × USD price path. Overlay participation while retaining dated revisits, recency and nested relativity. Five alternatives share local source data, backdrop selection and Earlier/Later paging:

1. **Volume Rails:** selected-window allocated-volume profile rendered as horizontal lines; thickness/opacity encode relative concentration. The complete-window profile is retrospective and must not be interpreted as already known at the left edge.
2. **Rolling Ribbons:** equal observation-count slices, volume-weighted 20–80% and 40–60% VWAP envelopes. These are descriptive distributions, not confidence/prediction intervals. A short window can have collapsed envelopes.
3. **Revisit Threads:** consecutive same-band VWAP assignments become sampled visit episodes. Circle size grows with visit volume; dotted connectors are returns, not intervening occupancy or exact boundary crossings. Only the busiest bands are drawn for legibility.
4. **Time–Price Heatmap:** time-slice × price-band cells; intensity encodes allocated shares relative to the largest selected-window cell. Cell colors across different backdrops are not an absolute common volume scale.
5. **Nested Profiles:** full-window, last 60/15 supplied minute bars or last 21/5 supplied daily bars. Each profile is normalized to its own peak to compare distribution shape; widths do not compare absolute volume. Short histories may make profiles identical; labels deliberately say bars, not elapsed minutes/sessions.

## Nested trend overlay

One shared toggle now draws fine (5-bar), middle (15-bar) and broad (45-bar) past-only EMA trend lines. Rising slope is green, falling slope red and flat neutral. Width distinguishes scale; broad is thick and dashed. Small perpendicular ticks mark a sign change at its first knowable bar. Arrows beside the chart retain simultaneous state: fine up with middle/broad down is a local countertrend rise, not a broad reversal.

Each EMA seeds with the first span closes, then applies alpha=2/(span+1). It is unavailable before that seed. Direction is the difference between consecutive EMA observations, with a 1e-10 flat tolerance. This is descriptive smoothed price direction, not signed flow, a calibrated momentum signal or a validated reversal detector. The original close path and density remain visible.

The calculation uses only source observations through the selected backdrop end, including prior available warmup bars outside its left edge. Earlier/Later paging never consumes later bars. Spans count supplied bars, not elapsed time or certified sessions. No label-only peak/valley backdating or future swing confirmation is used in this displayed model. Old experimental pivot-classification helpers remain for research/test compatibility but are not the overlay.

These fixed 5/15/45 defaults are illustrative presentation settings, not optimized thresholds. Child turns do not promote parent direction. EMA values can lie outside the visible price domain; those portions are clipped without changing the actual-price domain. Arrow state may therefore remain available when part of a line is offscreen. Canonical event recognition, calibration and independent source acceptance are separate gates.

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

The suite uses synthetic values only. It tests input rejection, immutable inputs, paging, pivot confirmation timing, prefix replay, ambiguous candles, allocation conservation and construction of all five SVG models at 320/736 px across five backdrop sizes. DOM construction is **not a browser layout test**. Browser launch in the author container failed because Chromium process sockets were not permitted; no screenshot or browser-interaction pass is claimed. Independent exact-head browser/domain CI remains pending with B01; generic repository CI is not evidence of this suite unless its logs execute it.

## Retained scope and handoff

Existing parent source/falsification obligations remain open. Reuse #108 for canonical adoption, #148/#152 for data/quality, #98 for independent traversal acceptance, and #265/PR266 for the premarket operator consumer. No polling, source store, trade execution, release, automatic merge or shared workflow change is part of this increment. Selection among models and real source/browser acceptance precede production integration.
