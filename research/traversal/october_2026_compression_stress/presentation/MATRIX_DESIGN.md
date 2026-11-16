# Traversal matrices: questions, evidence and display contract

Status: Zone Participation and Nested Context have offline research implementations; Turn Episodes remains a presentation design. This is not a canonical schema. Owner B06 #144 / draft PR145. Source charts remain descriptive; no forecasts or composite reversal score. This document records the next presentation contract within the existing research scope.

## Display composition

One shared as-of, source snapshot, ticker, USD basis, selected backdrop and selected granularity. A familiar price/time chart stays above ONE selected matrix; selecting a matrix row highlights its zone or episode and exposes the relevant existing chart view. Do not overlay all eight models. On phones, stack the chart and selected-row evidence; keep the same analytical aggregation as desktop.

Three matrices answer different questions:

1. **Zone participation**: frozen price intervals as rows, selected nonoverlapping time blocks as columns. Cell display mode is shares, percentage of window shares, sampled occupancy or visits; never mix units in one color scale. Keep an absolute-share total and unallocated amount visible. Row selection exposes recent vs earlier participation and traversal evidence.
2. **Nested context**: horizons as rows, the same descriptive quantities as columns. Position, signed change, speed, turnover, movement per turnover, range-width change and confirmed structure remain distinct. Selected child and parent windows share an as-of. Overlapping horizons are comparisons, not additive totals.
3. **Turn episodes**: candidate/recognized changes as rows; before/after measurements as columns. Event definition, recognition label, preceding block, completed following evidence and unresolved future outcome are explicit. EMA slope switches, block-return sign switches and structural changes have different event types. Do not label an unresolved turn successful.

Zone Participation is now implemented with fixed USD bands and bar-VWAP allocation estimates. Exact dwell and an event ledger remain absent. Nested Context now compares common-price position, signed distances, own-window movement/turnover, range change and confirmed structure, with partial/lagged rows explicit. Turn Episodes is still proposed.

## What each dimension exposes

| Dimension | Display | Valuable observation | Interpretation to investigate | Counterexample / limit |
|---|---|---|---|---|
| Position | Child interval inside fixed parent interval; close and VWAP separately | Where price sits relative to earlier extremes | Recovery toward a prior ceiling or movement beyond a prior floor | Position can rise because a rolling floor fell; use fixed reference |
| Participation | Shares and signed percentage-point change in share of window total | Where turnover concentrated | New concentration at higher/lower levels | High turnover does not identify new holders, intent or net inflow |
| Occupancy | Qualified bar-sample count / eligible samples; actual elapsed occupancy only with justified source support | Repeated sampled presence | Sustained trading versus a brief pass | Whole minute duration cannot be assigned to its VWAP price |
| Revisits | Episode count, last visit time and shares by episode | One large encounter versus repeated returns | Repeated engagement or loss of participation | Missing minutes break episode certainty; no exact boundary order from OHLC |
| Migration | Earlier/recent weighted price distribution on common price bins | Trading concentration moved above/below its earlier location | Repricing of the active range | Independently normalized profiles hide absolute-size differences |
| Direction and speed | Signed USD/bar, later USD/elapsed-minute after clock qualification | Net direction and rate of travel | Advancing/declining movement strengthening or weakening | Lower turnover alone is not acceleration; gaps need separate treatment |
| Movement per turnover | Signed net USD per 1M shares alongside total shares | Displacement relative to trading activity | Less/more turnover accompanies a given move | Not causal impact, buy/sell imbalance or gross internal path |
| Compression / expansion | USD width, midpoint-normalized width and signed change against prior disjoint window | Occupied range narrows/widens | Confinement versus greater movement | No directional forecast; an old extreme leaving a window can narrow it |
| Structure | Confirmed high/low sequence and recognition delay | Progression of floors and ceilings | A local move obtains structural confirmation | Confirmation lag and ambiguous outside candles remain visible |

## Existing views mapped to matrix questions

| Existing view | Primary contribution | What it adds beyond the other views |
|---|---|---|
| Volume Rails | Zone participation totals | Compact full-backdrop distribution by price |
| Rolling Ribbons | Distribution migration | Continuous central-concentration trajectory |
| Revisit Threads | Visit chronology | Separates turnover into sampled return episodes |
| Time–Price Heatmap | Zone-by-time participation | Locates old versus newly active concentration |
| Nested Profiles | Recent versus broader shape | Compares distributions at nested horizons |
| Compression / Expansion | Range environment | Separates width change from price direction |
| Swing Structure | Confirmed floors/ceilings | Later structural progression without duplicating price line |
| Movement / Shares & Turns | Movement versus turnover | Distinguishes block direction, price speed and volume-normalized movement |

## Arithmetic and denominator requirements

- Fixed-parent position = 100*(P-L)/(H-L); retain values outside 0–100, null for zero width. Show signed distance from high as P-H and 100*(P/H-1), negative below high. Distance from low uses P-L and 100*(P/L-1).
- Zone volume share = allocated zone shares / total selected-window shares, including unallocated shares in denominator. Sum zones plus unallocated to total. A share change is signed percentage points, separately from absolute share-count change. Compare like time blocks; unequal durations require explicit labels and rates.
- Current whole-bar VWAP allocation is an estimate. Sampled occupancy = assigned qualified samples / eligible observed samples, with missing/invalid counts exposed. Do not call this exact time at price. Genuine traded-at-price/dwell requires finer entitled source observations and an explicit estimator.
- Revisits count consecutive same-band assignments; gaps must flag discontinuity rather than join an episode silently. Zone bounds freeze for comparison; later revisions get new references, not retrospectively recentered zones.
- Completed-block movement = last close minus first open. Divide by block shares/1M for current movement/turnover. Keep time speed separate; current implementation counts supplied bars, not elapsed minutes. Net-zero can conceal large internal excursions. Gross sampled travel and cross-block gaps must be separately defined before implementation.
- Use common zone boundaries and explicit shared/independent color scales. Locking bins alone does not make unequal horizons or volumes comparable. Never sum nested windows or multiply corroboration counts across transforms of the same input.
- Source effective/observed/available/ingested times, input hash, model configuration, missingness, TTD and completed-bar state must accompany accepted production projections through existing owner contracts. Unknown fields stay null, not neutral.

## Reading combinations without inventing a score

| Observed combination | What it supports describing | What would strengthen / weaken the interpretation |
|---|---|---|
| Heavy turnover; little net movement; repeated same-zone samples | High participation with limited net progress | Follow with direction, range exit and retest; both absorption and opposing churn remain possible |
| Distribution migrates upward; completed returns positive; later higher low/high | Upward repricing with subsequent local structural confirmation | Holding the higher zone strengthens; rapid return below earlier floor weakens |
| Range narrows; turnover decreases; direction remains mixed | Reduced activity and confinement | Only subsequent expansion establishes direction; low-liquidity absence can mimic compression |
| Negative returns accelerate; active concentration shifts lower | Downward displacement and participation migration | Sustained reclaim of prior zone weakens continuation description; it does not supply a probability |
| Fine-scale upward turn; broader lower highs/lows persist | Local rebound inside broader declining structure | Broader floor/ceiling progression must change before calling broad reversal |

## Ordered implementation acceptance

1. Fixed-zone projection and denominator conservation, unallocated samples, gap/coverage guards and exact input identity; add zone participation matrix first. Do not register a new shared schema here.
2. Linked selection highlights matching evidence in existing heatmap/rails/threads without changing calculations. Shared source, units, as-of, bins and scale labels survive backdrop changes; phone/desktop numeric equality is tested.
3. Nested context rows use fixed reference identities, signed deltas and nonadditive horizons; source freshness and missingness stay visible.
4. Turn episode comparison separates event types and first recognition from later outcomes; deterministic prefix replay and right-censoring required. No hindsight boundary changes or automatic probability.
5. B01 independent exact-head real browser/control checks; B02 source/clock/quality and B06 canonical adoption gates remain separate. Synthetic arithmetic tests do not certify market inference.

Next action: independently validate both implemented matrices at exact head, then implement Turn Episodes with distinct recognition and outcome clocks. Canonical input identities and source-clock acceptance remain upstream gates; preserve producer and ingestion ownership.
