# CRWV historical range corpus

Dated research replay from Massive adjusted one-minute aggregates, October 1–28, 2026. The final October 28 observation is 11:34 ET; this is not a live feed. Nineteen full regular sessions and one partial session supply 7,534 regular-session bars. Extended-hours source rows are preserved but excluded from replay.

[CRWV.range-patterns.jsonl](CRWV.range-patterns.jsonl) contains 259 candidate range episodes and 100 completed close-to-close traversals. [summary.json](summary.json) gives counts; [pattern-index.json](pattern-index.json) groups events by formation position and directional efficiency. [manifest.json](manifest.json) records source requests and SHA-256 checksums. These are dated research fixtures, not the canonical ingestion store.

## Replay

From this directory, with Python 3.9+ and the parent battle_matrix.py:

```bash
python -m unittest test_range_replay -v
python range_replay.py --minutes CRWV-minute-bars.csv --daily CRWV-daily-bars.csv --out CRWV.range-patterns.jsonl --ticker CRWV
```

Appending the same input is idempotent: the verified rerun added zero revisions. Changed observations create new revisions linked by supersedes_revision_id. Event IDs identify the ticker, session, frozen zone and configuration; hashes preserve input and implementation identity.

Ranges form from 30 completed contiguous minute bars. Confirmed local pivots cluster into lower and upper bands; each cluster needs two pivots separated by at least three minutes. Bands freeze before evaluation. Episodes run for at most 30 minutes, ending earlier after two consecutive closes outside the outer band by two cents. Evaluation episodes do not overlap; formation windows can overlap. These choices are heuristics, not optimized thresholds.

## Record contract

| Fields | Meaning |
|---|---|
| zone, formed_from, frozen_at | Frozen band coordinates, width, pivot evidence and confirmation times |
| features_at_freeze | Formation-only position, path and directional efficiency |
| outcome.flow | Up/down range travel per dollar turnover; score above 1 means upward travel was easier, below 1 downward; insufficient directional samples remain null |
| outcome.activity, *_band_activity | Shares and VWAP-times-shares gross dollar activity; band assignment uses whole-bar VWAP |
| volume_pct_adv20, same_time_rvol | Prior daily volume scale and matching-clock participation; missing history remains null |
| upper_encounters, lower_encounters | Debounced contact episodes, activity and observed response; contacts are not independent trials |
| completed_close_traversals | Alternating close-confirmed boundary-to-boundary legs, elapsed time and turnover |
| first_passage | Opposite target versus outside failure from a boundary anchor; ambiguous ordering and timeout kept separate |
| quality, input_hash, revision_id | Gaps, censoring, source limitations and reproducibility |

The efficiency ratio uses a five-minute half-life and requires at least three observations and effective sample size two in each direction. It measures movement per gross turnover, not aggressive buying/selling. Range-width and daily-dollar normalization cancel from the ratio; participation and net path progress remain separate fields. Same-time participation requires at least five prior complete observed sessions and excludes today's session.

## Interpretation limits

The detector produced 219 confirmed range breaks, 30 horizon timeouts, nine session-end timeouts and one partial episode. Many candidates are fragile; these counts do not demonstrate a trading edge. First-passage opposite-band-first count (42) and complete traversal count (100) use different anchors and definitions and are not interchangeable.

A ceiling without contact is untested, not rejected. OHLC bars cannot order both barriers touched in the same minute. Volume assignment is approximate, not actual trade-level volume at price; no signed order flow, executable spread, slippage or profit inference is provided. The source is a vendor historical revision, not an archived point-in-time feed: construction avoids future formation data, but original availability timestamps are unknown. Thresholds and index buckets are uncalibrated; held-out sessions/tickers and execution costs are required before predictive use.

Twelve replay tests pass, covering confirmed pivots, gaps, future-edit/prefix stability, ambiguity, censoring, traversal volume, no-contact vocabulary, contact debouncing, revision idempotence, ticker generality and exclusion of current-day volume from baselines. Unit tests establish implementation behavior, not forecast accuracy. The reusable incremental tool is a separate delegated scope.
