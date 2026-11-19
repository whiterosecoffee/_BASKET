# B06 #144 acceptance cases and historical falsification gates

**Status:** Test specification, not executed regression results. Source-of-truth: [README](README.md). Never convert an expected result into a claimed observed outcome without canonical, time-bounded source evidence.

## Minimal event-sequence test matrix (synthetic state examples only; NO market-history copies)

| Case | Completed input sequence, as known at each step | Expected event transitions | Negative assertion |
|---|---|---|---|
| T01 | Freeze range low=100, high=105 at T0; T1 touches low, T2 rises to 102; T3 closes below frozen low | contact→stabilization_attempt→failed_stabilization at T3 | T1/T2 cannot be called failed at T2 |
| T02 | Freeze same range; T1 touches, T2 rebounds, T3 holds above defended low and completes predeclared higher-low+higher-high test | candidate→defense→local reversal_confirmed at T3 | No higher-timeframe reversal inference |
| T03 | T1 and T2 oscillate ±2 with flat net close, high turnover | low path efficiency; chop/undetermined flow | Cannot equate flat net return with passive absorption |
| T04 | T1 new low, falling bp/USD billion across three contacts, but no rebound confirmation before horizon ends | absorption_candidate→unresolved | Cannot mark success just because impact falls |
| T05 | One 1-minute candle high breaches ceiling and low breaches floor | ambiguous intrabar crossing | Cannot assign order of touch, buy/sell or stop trigger |
| T06 | Child 5m range reverses upward while parent 60m and 20d remain bearish | local reversal event + bearish parent state | Must not promote to global trend reversal |
| T07 | Two overlapping ranges share same source bar IDs | separate range references, common source ID | No summation of turnover twice |
| T08 | Identical source snapshot and model configuration replayed twice | byte-identical deterministic event identity and output | No duplicate appended event |
| T09 | Source issues correction; replacement includes original source ID and revision | new correction/supersession event | Original observation/event immutable |
| T10 | Missing 20 prior eligible same-clock sessions, unavailable signed trade classification | relative activity=null, OFI=null, reason attached | No neutral values fabricated |
| T11 | Source returned fractional shares, VWAP outside [bar low,bar high], auction spike | explicit source quality result or blocked | Do not normalize or discard without B02-approved contract |
| T12 | Daylight saving transition, exchange holiday, one skipped minute and future-dated bar | correct America/New_York session gate, gap reject, future reject | No fixed UTC offset or fabricated bars |
| T13 | Bad upside/noise threshold produces many stabilization events on range-bound control | high false-positive count in baseline | Cannot cherry-pick ticker failures/successes |
| T14 | Last candidate still open at evaluation cutoff | right-censored outcome | Cannot count as failure or success |
| T15 | Previously rejected candidate subsequently makes higher high | new event referencing prior attempt and observed time | Never retroactively erase earlier rejection |
| T16 | Ticker X gaps up 4% at open, barely changes during RTH | overnight gap distinguished from RTH travel | No overnight notional included in RTH return/impact |

## Required historical cohort

- Universe fixed **before evaluation**: primary AMD, NVDA, CRWV, AVGO, ORCL, INTC, AAOI; controls QQQ, SPY, SMH, MAGS; context candidates MU, MSFT, GOOG, AMZN, HYG, IEF and USO.
- October all complete eligible sessions, with dedicated investigation Oct 14, 16, 22 and 30. Include subsequent Nov 2 and Nov 3 **only as retrospective/descriptive cases unless a verifiable earlier frozen parameter revision exists**.
- Need a source coverage table for every ticker × trading day × timeframe: expected bars, actual complete RTH bars, missing count and UTC intervals, provider and adjusted/raw policy, snapshot hash, first availability and ingestion times, TTD, auction handling, anomaly flags. Missing rows routed via B00 #148 / B02 #152 (no copied bars or blind backfill).
- For every qualifying candidate, emit immutable as-of evidence links and later label references; report total detection candidates, confirmed recoveries, failed stabilizations, unresolved, excluded-quality, sensitivity by timeframe. Include ticker-day clustering so many overlapping five-minute attempts do not inflate denominators.
- Compare three hypotheses on **same event cohort**: H0 price-only ATR/VWAP baseline; H1 signed price movement vs dollar-notional/path efficiency; H2 boundary persistence/retest failures. Compare H1+H2 only after independent metrics, using *incremental* gain in precision/recall and decision delay relative to H0. Record false positives, missed rebounds and counterexamples, not only dramatic selloffs.
- Include first-bar-of-day and last-auction separated to ensure clock-aligned volume benchmarks are not biased. Trade aggressor balance and depth null without entitled quotes/trades.
- A later B07 study, not #144, estimates probabilities/expected performance with genuine walk-forward folds, transaction costs, rebound opportunity cost and suitable multiple-testing controls.

## Orchestration gate matrix
| Gate | Owner | Must exist before claim |
|---|---|---|
| G0 canonical logical resolution | B00 #148 | verifiable as-of resolver, explicit pre/post-cutover behavior |
| G1 historical quality and coverage | B02 #152 and ingestion owner | reproducible complete bar manifest, anomaly resolution/quality flags, source IDs |
| G2 historical event recognition | B06 #144 | deterministic all-event enumeration and test report against above cases |
| G3 canonical integration | B06 #108/PR109, with #149/PR150 inputs | shared engine adapter after G2, no duplicate engine/poller |
| G4 independent validation | B01 | exact-head CI and migration/regression checks |
| G5 inference | B07 #93 | walk-forward calibrated performance; *not* assumed from G2 |
| G6 delivery | B08 | only when validated and source freshness/runtime proved |

Blocking states must be machine-readable: `BLOCKED_CANONICAL_DATA`, `INSUFFICIENT_HISTORY`, `UNENTITLED_FLOW`, `SOURCE_QUALITY_AMBIGUOUS`, `UNRESOLVED_EVENT`, `TEST_NOT_RUN`.

**Evidence rule:** An acceptance case existing in this document is `specified`, not `passed`. Record executed commands, counts, environment and exact commit before upgrading status.
