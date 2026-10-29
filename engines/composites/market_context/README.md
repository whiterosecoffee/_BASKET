# Basket market-context subroutine

Entry point: `context.analyze(registry, current, previous, mode, policy)`.
Owner: cross-market composites (B17), worker #100. Python 3.10+, standard library only.

This is a callable consumer of dated observations, not a quote server, trading bot,
causal attribution model or probability forecaster. It writes no B02 market stores.

## Run

From repository root:

```bash
python engines/composites/market_context/context.py plan --registry research/composites/market_context/registry.working.json
python engines/composites/market_context/context.py report --registry research/composites/market_context/registry.working.json --current research/composites/market_context/fixtures/basket.json --previous research/composites/market_context/fixtures/midday.json --mode research
python -m unittest discover -s engines/composites/market_context/tests -v
```

Default mode is strict. Captured Massive responses did not explicitly establish
quote entitlement, so their usable prices require explicit `--mode research` and
reports remain provisional. Do not promote them by changing a label without
provider proof. Some OTC quotes may have fresh session updates and old trade bars;
the older trade bar prevents a false freshness claim.

## What it looks at

| Layer | Measures | Purpose |
|---|---|---|
| Market | QQQ, SPY, RSP, IWM | Growth pressure versus broad participation/rotation |
| Sectors | SOXX/SMH, XLK, IGV, XLC, XLI, XLU, XLF | Sector-relative leadership and supply-chain breadth |
| Basket | Fixed membership denominator, weighted/equal price return, advancers, decliners, dispersion | Whole configured research universe; never substitute only available winners |
| Tickers | Prior-close return, prior-snapshot return, relative QQQ/sector return, open/VWAP distance, session range position | Distinguish recovery, relative strength and ongoing weakness |
| Trading activity | Snapshot volume times VWAP | Labeled gross dollar-turnover proxy; not net inflow or synchronized RVOL |
| Credit | Actual HY/IG spreads, changes | Funding stability; HYG price is context only |
| Rates/dollar | Nominal/real yields, breakevens, DXY | Discount-rate/inflation pressure |
| Liquidity | SOFR-IORB, reserves | Funding conditions; no duplicate net-liquidity identities |
| Energy | WTI/ULSD | Cost pressure; falling oil not automatically bullish |
| Sentiment | VIX, VIX3M, equity-only put/call | Volatility, term structure, crowding |
| Events | Official release times and issuer evidence supplied by B03 | Explain observation context; never infer causation from simultaneity |

`refresh_plan()` builds batch symbol requests from the registry plus benchmarks and
group proxies, lists unresolved symbols and source-series requirements, and returns
a scheduling proposal. An entitled persistent producer and exchange calendar belong
to B02/B08. No scheduler is installed by this component.

## Deltas and state

- Percent return = `100 * (current / baseline - 1)`.
- Relative return = ticker return minus aligned benchmark return, in percentage
  points. No beta, regression residual, or causal claim is implied.
- Prior-snapshot aggregate uses only the intersection available at both captures,
  with coverage measured against the full configured basket. It never subtracts
  changing-universe averages.
- `window_deltas()` supports 5/15/60 minute baselines. It requires the same session,
  prior source availability, and a baseline no more than two minutes older than
  requested. Missing windows stay missing. No interpolation into missing bars.
- `recovering_outperformer`: interval gain >1% and interval QQQ-relative gain >1pp.
  `weak_underperformer`: interval QQQ-relative return below -1pp. Otherwise mixed.
  These are explicit heuristic labels, not calibrated probabilities.
- Day and group means require 75% configured weight coverage. Below that, the
  observed-subset mean is shown separately and the full-basket mean is null.
- Macro policy preserves 21 indicators/seven pillars from the prior schema. A
  pillar needs 60% internal coverage; full score needs 75% raw weight coverage,
  80% published pillar weight, and published credit/rates. Growth-shock overrides
  cap favorable falling-yield/oil readings at neutral. Raw scores remain visible.
- `macro_impulse()` compares matched factor scores and records coverage. It does
  not certify a five-session horizon; caller must verify the exchange calendar.

## Input contract

`basket.market_context_input@1` has `snapshot_id`, `as_of`, `available_at`,
`ingested_at`, `session`, `quotes`, `macros`, `supersedes`. Each quote requires USD
price, prior close, timestamp, first-known capture bound, source, session,
entitlement/delay, return-basis label and prior-close baseline ID. Optional fields
are open, VWAP, high, low, volume and actual last-trade-bar timestamp. Raw source
CSV is retained in the research fixtures. This is a B17-local contract, not an
unilaterally added shared schema.

Unknown, conflicting, future, stale or misaligned prices cannot silently earn a
neutral score. Quote age is 120 seconds plus documented delay; session updates
cannot freshen an older executed-trade bar. A benchmark comparison requires
matching currency/basis/baseline and timestamps aligned within 120 seconds.

The registry is versioned/hashes into every report. It must have been available
and effective at the current snapshot unless `--retrospective` is explicitly set.
Current-membership comparisons against older snapshots are labeled as matched
current-universe diagnostics, not a historical membership backtest.

## Persistence and restart

```bash
python engines/composites/market_context/context.py append --db /path/to/consumer-context.sqlite --snapshot research/composites/market_context/fixtures/basket.json
python engines/composites/market_context/context.py replay --db /path/to/consumer-context.sqlite --as-of 2026-10-29T16:45:00Z --known-at 2026-10-29T16:46:00Z
```

SQLite transaction locking serializes append operations. Duplicate identical IDs
are idempotent; changed content under an existing ID is rejected. Corrections use
a new ID, preserve capture time, arrive later and supersede the latest revision;
forks are rejected. Replay filters both first availability and ingestion so later
corrections cannot enter earlier knowledge. Historical retention is separate from
current quote freshness. This consumer journal does not replace B02's canonical
observation revision contract or install hosted storage.

## Integration boundary

B02: entitled producer, trustworthy last-trade/quote timestamps, FX, baselines and
historical/rolling source data. B06: multi-window traversal/range outputs. B03:
source-backed events. B00: approve authoritative full registry/sector mapping and
shared-contract publication. B01: independently execute these tests at PR head.
B08: persistent scheduler/serving. Until these are connected, macro coverage and
some rolling windows will stay missing. No continuous live service is claimed.
