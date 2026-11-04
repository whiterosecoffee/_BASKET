# ORCL Range Traversal: index, freshness gate and output contract

Status: v0 (unverified, unrun, untested, unmeasured). Issue #81. Reusable for any TARGET by swapping params; shipped for ORCL.
Partition logic: the shared method lives in `BAND_METHOD.md`; each window has its own file; cross-window reading and benchmark divergence are separate vectors. Valuation, financing, partnerships and catalysts belong to other vectors and owners (#76). A window file never redefines the shared method; it only states what is specific to its horizon.
Sibling vector set: `research/ORCL/Forward_Multiple/` (issue #80, separate branch until merged).
Aligned to: tracker panels `traversal` and `market` in `orchestration/ticker_trackers/orcl.json` (#75, #77); baseline engine `engines/traversal/range.py`.

## FILES (run order)
1. `BAND_METHOD.md`: how bands, touches, dwell, dollar volume and regime are built (shared by every window)
2. `TODAY.md`: the current regular session
3. `72H.md`: trailing 72 clock hours, regular-session bars only
4. `10D.md`: trailing 10 completed trading sessions
5. `CROSS_WINDOW.md`: nesting, confluence, conflict, transition events, ladder
6. `DIVERGENCE_OVERLAY.md`: the same three windows versus benchmarks

## PARAMS
- TARGET = ORCL
- BENCHMARKS = QQQ, NVDA, IBM, HYG, IEF, USO (same set as the tracker)
- TIMEZONE = America/New_York; CURRENCY = USD
- BARS = 5-minute regular-session bars for bands (78 per full session); daily bars for 10D endpoints
- Extended hours: reported separately, never merged into regular-session bands

## FRESHNESS GATE (runs before any window; blocks everything on failure)
1. State first which markets are open, closed or on holiday now, and TARGET's session phase.
2. Source priority: (a) repo stores `tickers/<TARGET>/history.jsonl` and `intraday/<date>.5m.jsonl` (B02); (b) the entitled Massive connector with the same endpoint and adjustment basis; (c) anything else is NON-ACTIONABLE. No web quotes for narrow intraday bands.
3. For every input print: source, endpoint, adjustment basis, feed delay, latest bar timestamp, data age, TTD.
4. `tickers/ORCL/` is absent on main today (B02 #61 and #62 own ingestion). Say so at the top. Use Massive only if it returns entitled, timestamped bars; otherwise stop and report the gap. Never fill missing bars.
5. TTDs (heuristic, v0): session window 300 s while open, matching the tracker `traversal` max age; after the close it is historical truth until the next first bar. 72H and 10D recompute when a new session's first bar arrives. TTD-expired data is historical, not current.

## OUTPUT CONTRACT (narrow lists, no wide tables)
1. Bottom line: where TARGET sits across the three windows and the single most important band.
2. Per window, three lines max: range and position, top band with dollar-volume method, regime.
3. Cross-window: nesting, confluence, conflict, transition events.
4. Divergence: one line per benchmark that is present, gaps listed.
5. Ranked scenarios (base, bull, bear) with the USD levels that move each. No probabilities.
6. Decision ladder: if price holds above X then Y; if it breaks X then Z; invalidation levels from the band method.
7. Data age, TTD, gaps, assumptions. Final line: "Next step: <queued action>".

## PROHIBITIONS
- No price, volume or consensus asserted without a timestamped source. No forecast probability, no price target.
- Separate verified facts, issuer claims, hypotheses and missing evidence.
- The three windows share bars; do not present them as independent confirmation.

## OPEN PARAMETERS (ghost nodes, not next)
- Band width multiplier, opening-range length, dwell threshold: see `BAND_METHOD.md` and `TODAY.md`.
- Whether 72H should mean three sessions; whether 10D should default to calendar days.
- Handoff to B06 for an executable implementation behind the `traversal` panel.
