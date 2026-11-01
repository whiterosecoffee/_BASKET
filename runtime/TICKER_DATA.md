# NVDA local ticker-data pattern

Pilot scope is **NVDA only**, until its patterns are refined. Other tickers are rejected. This is a local Python library and CLI, not a running worker, scheduler, quote service or valuation engine.

## One block, existing storage conventions

`TickerStore(root)` provides validated create/read/revise/retract over one JSONL journal at `<root>/tickers/NVDA/observations.jsonl`. It does not replace existing positional `history.jsonl`, `entity.json`, `events.json` or `relationships.json`. `legacy_bars` reads the existing eight-field daily format without manufacturing missing availability evidence.

The observation validator, canonical hash, replay and snapshot functions are recovered from PR #15 at `68146c1443dc485d2e5f7e811dbfcd6d76b9ed77`. `observations.py` and its domain tests are byte-identical to that source (Git blobs `e05de0422ad8da480ba36bd915963c0515670a34` and `dc5652cfe48317d500ca92af3377642ecbef66d7`). Its original append API remains unchanged. Use **TickerStore** for pilot writes: it adds idempotency, strict schemas, linear revision checks and atomic whole-file replacement. This is partial recovery, not acceptance of all #11 requirements or supersession of its remaining work.

Patterns borrowed: repository adapter / ports and adapters; Design by Contract; security-master identity separation; append-only correction and point-in-time replay. We borrow revision principles without adopting an event-processing platform.

| Option | Reuse | Immediate burden | Decision |
|---|---|---|---|
| Reuse journal + small local adapter | High | Low | Selected |
| Build a new general storage framework | Low | High | Rejected for this pilot |
| Add database/server now | Medium | Higher operations/migration cost | Defer until measured file-size/concurrency needs |

These are qualitative design judgments, not measured performance scores. Review the choice when the one-week pilot no longer fits memory or atomic full-file replacement becomes costly.

## Contracts

`schemas/ticker-data.v1.json` defines observation input and `$defs.result` for output. Persisted records add a computed `record_id`; callers cannot assign it. Input requires identity, kind, source and source record identity, economic observation time, first verified availability, local ingestion time, currency, expiry policy and typed value.

Two kinds are supported:
- `market_bar`: explicitly one-minute or daily aggregate, adjustment basis, OHLCV and optional provider VWAP/trade count. Bars are never labeled individual trade ticks.
- `financial_fact`: concept/taxonomy, reporting period, original units, amount, reported/calculated/guidance/estimate basis, source URL and excerpt. `period_start` can be null when not verified. This first duration-fact profile is not yet a complete balance-sheet, segment or multicurrency contract.

Public methods:
```python
from runtime.ticker_data import TickerStore
store = TickerStore('/path/to/local/data')
created = store.put(observation)
current = created['records'][0]
corrected = dict(observation, supersedes=current['record_id'])
# Change the value and use truthful new availability/ingestion times.
revised = store.put(corrected, expected_head=current['record_id'])
historical = store.read('2026-11-01T01:52:03Z', kind='market_bar')
```

- `put_many(observations, expected_heads=None)` validates and commits the entire batch atomically. Invalid rows or conflicts commit nothing.
- `read(as_of, kind=None, start=None, end=None, include_retracted=False)` uses public availability **and** local ingestion cutoffs. Ranges are start-inclusive/end-exclusive. Historical snapshots do not imply currently fresh prices.
- A changed value requires `supersedes` and `expected_head` naming the current record. Repeating the same economic content returns `unchanged`, retaining the first accepted availability. Later retrieval timestamps or raw-response fingerprints alone do not create new economic events.
- Retraction is a revision with `retracted: true`, `value: null` and the current head. Previous states remain replayable. No physical-delete/retention job is enabled.
- Results contain schema/version, entity, status, records, snapshot hash and structured errors. `no_data` is an empty local query, **not** a successful source scan or verified complete coverage. Failed reads are `rejected`, never silently empty.

The exclusive lock coordinates users of this adapter; it cannot prevent arbitrary outside processes from modifying a file. Writers must use the interface. A stale lock requires inspection rather than automatic takeover. Atomic replacement preserves the prior complete file on a failed write. Filesystem durability after OS/power failure and network-filesystem behavior are not qualified. The pilot rewrites the bounded journal and is not designed for full trade-tick scale.

## Source adapters and timestamps

`massive_bar` accepts a successful archived NVDA REST aggregate response with explicit interval/basis and timestamps. Pending pagination is rejected. `massive_csv_observations` adapts the connected Massive tool's `v,vw,o,c,h,l,t,n` CSV output and preserves its SHA-256 fingerprint. The CSV lacks the original REST response status/pagination metadata; the caller must preserve request provenance separately. Neither adapter independently establishes complete exchange coverage.

In connected-tool imports, `available_at` is the conservative **first verified availability bound at retrieval**, not a claim about original vendor publication time. `ttd_seconds: 0` prevents historical captures from being promoted to live values. The revenue fixture uses the same conservative bound, not an invented 2024 release time. The observed date for financial facts is the period-end date represented at UTC midnight; it is not a precise economic-event timestamp. Raw source date/period remains in the value.

No forward fill, missing-bar fabrication or implicit currency/adjustment conversion. Missing qualifying trades may produce no bar. Partnerships, issuer/security mapping, corporate actions, instant financial facts, FX and valuation formulas remain separate unimplemented consumer contracts; do not infer them from this pilot.

## Actual NVDA demonstration

Source: connected Massive aggregate endpoint `/v2/aggs/ticker/NVDA/range/1/minute/2026-10-26/2026-10-30`, `adjusted=false`, ascending, limit 50000. Returned **4,690** minute bars across the five dates, including extended hours; Friday has **953**. Each date contains **390** records between 09:30 and 16:00 America/New_York. This checks observed regular-session minute counts; independent exchange/provider correction reconciliation remains unverified.

The executed local capture is `/workspace/nvda-data/tickers/NVDA/observations.jsonl`, with 4,690 bars plus one historical reported revenue fact. The data is in this execution workspace, **not installed on the user's workstation**. Raw CSV: `/workspace/nvda-massive-2026-10-26_30.csv`. Market data is not committed to the public repo; only provenance/counts/hashes are in `fixtures/nvda/capture-evidence.json`. Raw and journal files need transfer to durable user-controlled storage for use after this environment expires.

Actual commands:
```sh
python runtime/ticker_data.py --root /workspace/nvda-data import-massive --input /workspace/nvda-massive-2026-10-26_30.csv --retrieved-at 2026-11-01T01:52:03Z --adjustment-basis unadjusted
# Same command repeated: unchanged, 4,690 records, no duplicates.
python runtime/ticker_data.py --root /workspace/nvda-data put --input runtime/fixtures/nvda/revenue.json
python runtime/ticker_data.py --root /workspace/nvda-data read --as-of 2026-11-01T01:52:03Z
python -m unittest discover -s runtime -p 'test_*.py' -v
```

The historical NVIDIA revenue fixture is **USD 35,082 million**, quarter ended 2024-10-27. Source: https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-third-quarter-fiscal-2025 . It demonstrates storing a reported fact, not a verified SEC/XBRL extraction engine. The initially attempted investor-relations URL returned 404; the newsroom release was retrieved successfully. Synthetic prices in unit tests are clearly labeled and are not imported as real data.

## Refinement sequence

1. Review the user's separate NVDA conversation when provided; this session cannot browse other ChatGPT Project conversations by title.
2. Refine this NVDA contract against real local consumer queries and independent source checks; keep other tickers disabled.
3. Qualify a durable local installation, source refresh and retention before claiming an autonomous maintained feed. Keep only the requested completed week in the initial capture; do not purge pre-existing histories.
4. Only then decide which additional financial/evidence formulas deserve a separate reusable block and acceptance fixtures. No valuation or trading claim follows from successful persistence.
