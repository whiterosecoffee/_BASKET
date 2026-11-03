# B06 two-track receiver prompt: relative position and movement

Destination: _BASKET master orchestrator, existing issue #144, branch work/144-october-compression-stress, draft PR #145. This conversation retains the same issue and branch. A NEW conversation must bootstrap a NEW issue and branch following AGENTS.md and orchestration/sparks.json.

## Objective
Build a reusable, source-verifiable multi-scale battle-range signal that measures where price is within multiple overlapping ranges and how direction, velocity, participation, impact, chop and boundary persistence are changing. Tie two tracks together:
(A) Historical chronological classification of October 2026 and November 2 RTH battle transitions, including candidate absorption, failed stabilization, resumed selling and genuine local reversal.
(B) Forward prefix replay of November 3 RTH with definitions frozen independently of later bars, ranking AMD, NVDA, CRWV, AVGO, ORCL, INTC and AAOI by confirmed recovery quality, rebound room and remaining downside. User is liquid comparing short-term entries; avoid inventing calibrated odds.

## Existing system: inspect and reuse
B06 main engines/traversal/range.py; issue #108/PR109 canonical traversal; B10 #95/PR99 local event journal; #92 signal proposals; B17 #100/PR101 market context; B02 market ingestion and TTD; B07 #93 calibration; B00 schemas and registry; B01 CI. Inspect current main, open PR changed files, and ownership before any shared implementation. This branch is restricted to NEW research/traversal/october_2026_compression_stress/** files; other domains require handoffs, not modifications.

## Experimental measurement and states
Inputs: completed Massive 1m OHLCV (RTH 08:30-15:00 America/Chicago, 09:30-16:00 ET after US DST ends; retain UTC), split policy, source timestamps, same-clock historical baselines. Treat AH and premarket separately. Never call traded USD signed pressure. Without entitled trade/quote book, order-flow imbalance, depth and exact volume at price are null, not inferred.

Freeze battle boundaries at discovery, give immutable IDs, support nested/overlapping parent ranges. Frames: 1,5,15,30,60,390min; 5,20,200 completed sessions. Event ledger JSONL: range_created, boundary_contact, expansion, absorption_candidate, stabilization_attempt, rebound, rejection, boundary_breach, failed_stabilization, higher_low, reversal_candidate, reversal_confirmed, continuation, unresolved, correction. Outcome known only when its event is completed, never retroactively alter preceding observations.

Measure signed log return (bp), velocity and acceleration (bp/min), traded USD/min and same-clock relative activity, signed impact bp per USD billion (descriptive proxy), net/gross path efficiency, local and ancestor range position, attempt count, defended low and failure time, price-impact change over contacts, normalized peer residual vs QQQ/SMH/MAGS, auction/outlier/gap flags. Preserve source/effective/available/ingested times, input hash, Git SHA and model version. Do not double-count underlying trades across nested range projections.

## Study and validation
All-event historical replay Oct 1-30 and Nov 2 for a fixed benchmark universe: seven candidate tickers + QQQ SPY SMH MAGS and controls MU MSFT GOOG AMZN HYG IEF USO. Identify Oct 14/16/22/30 stress waves; separate macro factors vs sector beta vs company-specific residual. November 2 has already been inspected, so it is exploratory unless definitions had actually been frozen before that session. November 3 prefix replay must not use future bars to fit thresholds. Hold out dates and tickers for real walk-forward validation.

Test three competing detectors independently: (1) price-only trend and ATR/VWAP, (2) price efficiency vs dollar turnover and gross path, (3) repeated boundary defense and failure; then incremental combined value. Measure precision, false alarms, missed rebounds, latency, censored attempts, costs, spread/slippage, macro differences and sensitivity. Include closing auction, split, missing bars, duplicate corrections, changing volatility and DST tests. Preserve unresolved rather than inventing success.

## Required deliverables
1. A versioned experiment spec with frozen detection thresholds and measured historical sample, including coverage/gaps, source hashes and input timestamps.
2. Append-only event examples/fixtures (clearly distinguished from observed), deterministic source-to-event replay code or executable test fixture under owned research subtree, independently runnable unit tests and real execution logs.
3. As-of snapshot per ticker: local and parent range low/high/position, relative volume and impact, path efficiency, factor residual, contact and breach chronology, recovery status, downside distance to defended low, reference battle ceiling, evidence quality, macro context and uncertainty.
4. Two separately ranked short-term lists: (i) confirmed recovery strength and (ii) speculative bounce elasticity/downside risk. No numeric win probabilities unless calibrated by B07. Explain why ranks differ.
5. Report comparisons in Troy IL CST first, ET secondary; USD figures only, UTC in permanent records. Ranked chart plus compact table.
6. GitHub issue #144, branch work/144-october-compression-stress, draft PR #145. Record exact files, tests, commit, provenance, blockers and receiver handoffs; NEVER merge without authorization. Shared schema B00, CI B01, canonical B06 engine #108, data B02, calibration B07.

Prior art: auction/market profile (battle zones), Cont order-flow imbalance and book depth (when entitled), Kyle/Amihud impact (proxy limitations), Kaufman efficiency ratio (chop), dollar/volume event-time bars, Hasbrouck impact persistence, CUSUM/online change points, multifractal scaling, event sourcing/bitemporal interval graphs. Cite concepts at actual metric use, not simply as a bibliography.

Success means reproducible, point-in-time classification and honest ranking that does not call a short bounce a durable trend reversal. If coverage or entitlement is missing, report explicit nulls and do the independent work possible.
