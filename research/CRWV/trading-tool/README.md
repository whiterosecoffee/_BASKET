# Ticker range traversal tool

A reusable local component for **any ticker's completed one-minute OHLCV bars**. Run it on every capture; it preserves the raw observations, frozen range versions, boundary encounters, close traversals and per-minute matrix. It does not need a conversation to compute the next signal once its polling process is hosted. Python 3.10+; standard library only.

From the repository root, read the most recent locally stored matrix:

```bash
python research/CRWV/trading-tool/run.py show --db /persistent/basket/patterns.sqlite --ticker CRWV
```

`show` reports the stored data cutoff and its current age. **The included corpus stops Oct 28, 2026 at 11:34 ET and is historical.** No new market conclusion should use it as today's tape.

## Capture and replay

The standard adapter input is a JSON object with `ticker`, `currency`, `source`, `bars`, `daily`, `profiles`, `patterns`. `source` identifies provider, source_id, entitlement, observation_kind (`historical`, `delayed`, `realtime`), adjustment, retrieved_at (or ingested_at when retrieval is unknown), available_at and source hashes/commit where applicable. A bar has `t` (UTC epoch milliseconds at minute START), `o,h,l,c,v,vw`. Bars must be ordered and unique; all source revisions stay auditable. `daily` contains previous completed sessions; `profiles` supplies actual historical one-minute sessions. Missing groups use `[]`; missing derived metrics stay null. No SQL server or API credentials are needed for local replay.

```bash
python research/CRWV/trading-tool/run.py capture --input /persistent/basket/CRWV-input.json --db /persistent/basket/patterns.sqlite --as-of 2026-10-28T11:34:00-04:00
```

Each capture supplies the **full ordered prefix**, not just the newest bar. Identical observations produce zero new signals. No partial current minute is processed. One database can hold multiple tickers. Session changes reset active ranges; gaps invalidate them. Processed source/context changes halt without modifying prior history. After auditing a correction, `--rebuild` creates a new generation and links each revised signal to its predecessor. Never delete the original generation to hide an error.

Pinned PR69 corpus replay (obtain its separate source checkout at commit `6d82bccacaaba9855ef6bd27c64d72eb0514c8c9`; no duplicate dataset is committed here):

```bash
python research/CRWV/trading-tool/corpus.py --source research/CRWV/debt/2026-10-22/historical-ranges-2026-10-28 --out /tmp/CRWV-input.json
python research/CRWV/trading-tool/run.py replay --input /tmp/CRWV-input.json --db /persistent/basket/CRWV-replay.sqlite --retrospective-matches
```

The corpus adapter checks pinned CSV hashes and the historical manifest's pattern hash before reading. Historical `available_at` is unknown. Strict matching therefore returns no such records; the explicit `--retrospective-matches` option labels those examples as non-point-in-time. Matches are frozen at range formation, use only comparable formation features (position, 15-minute score, 30-minute path), exclude future outcome windows and other tickers, and attach outcomes only after ranking. They are descriptive analogues, never calibrated odds.

Export **all immutable generations** (use `export-input` instead of `export` to recover the last captured source JSON for replay without its original file):

```bash
python research/CRWV/trading-tool/run.py export --db /persistent/basket/patterns.sqlite --ticker CRWV --out /persistent/basket/CRWV-signals.jsonl
```

SQLite is the atomic source journal; JSONL is a regenerated export. SQLite transactions commit inputs/observations/signals/checkpoints together, serialize writers and roll back failed updates. UPDATE/DELETE triggers enforce append-only application use. Database filesystem owners can still alter files; this is not cryptographic tamper-proof storage. Keep the WAL and database on a durable local disk, not a shared network filesystem. Runtime owner must configure backups/retention; indefinitely retaining full capture inputs has storage cost.

## Compact matrix and interpretation

| Field | Meaning |
|---|---|
| lower / upper | Frozen repeated-pivot bands, not redrawn after outcomes |
| position | `(last − outer lower)/(outer upper − outer lower)`; can exceed 0–1 |
| S | Weighted upward movement per dollar / downward movement per dollar; center **1** |
| directional sample | Each side needs 3 bars and effective N≥2; otherwise S is null |
| Q | Signed endpoint progress / observed close-path travel, −1 to +1 |
| $ / shares | Gross 15-minute turnover; bar VWAP × shares approximation |
| ADV% | Window shares / prior 20-session average shares; missing history ⇒ null |
| clock RVOL | Actual same-clock window / prior completed-session windows; needs 5 comparable sessions |
| contacts / retreats | Debounced observed episodes; neighboring candles are not independent tests |
| traversals | Boundary-to-opposite-boundary CLOSE transitions and elapsed minutes |
| cutoff / age / quality | Completed-bar time, retrieval age, window gaps, vendor VWAP/OHLC discrepancies |

S>1 means upward movement was cheaper per observed turnover. It can coexist with negative net drift. ADV and range width cancel from S; activity and range position remain separate. S is not buying/selling imbalance, conviction, probability or a linear price-impact forecast. A one-sided burst produces null S instead of infinity. It still has direction/path/activity evidence.

Thirty contiguous minutes form a range from ≥2 separated confirmed low pivots and ≥2 high pivots. One subsequent bar confirms each pivot; it is already known at freeze. Two successive closes beyond the band plus $0.02 end that range. A successor receives a new ID. These tick-based parameters are **unfitted heuristics**, especially outside liquid US stocks. Shortened sessions are not fabricated into 390-minute volume profiles.

Contact requires actual OHLC overlap. A later retreat has a distinct event; touch and retreat inside one candle are order-ambiguous. Downward drift without a recent ceiling contact is `drifting_lower_ceiling_untested_5m`, not resistance rejection. Both-band candles carry unknown within-bar ordering. Close traversals miss intrabar crossings and do not imply achievable execution or profitable cycling.

## Autonomous polling, readiness and blockers

`poller.py` is a runnable **separately hosted** REST adapter with bounded pagination/current-day backfill, duplicate-safe restart, source-revision halt, exchange market-status handling and fresh/stale health output. It polls qualifying aggregate bars; it is not tick-by-tick tape or a WebSocket implementation. It consumes a host `MASSIVE_API_KEY`; ChatGPT's authenticated connector does not expose one. No secret is committed, copied or printed.

```bash
python research/CRWV/trading-tool/poller.py --ticker CRWV --db /persistent/basket/CRWV-poll.sqlite --context /persistent/basket/CRWV-context.json --health /persistent/basket/CRWV-health.json --feed-mode delay_unknown --interval 60 --cycles 0
```

`context.json` supplies `daily`, `profiles`, `patterns` (or empty lists). Pin it within a generation; revised processed context requires an audited rebuild. Use a separate database from historical replay because source identity differs. Start with `--cycles 1` for a bounded acceptance probe. A real service manager must supervise the indefinite command, mount durable storage, arrange credentials, backups and calendar checks, and restart on health failure. No process is launched by these files.

Backfill is bounded to the current ET day. Same-day restarts recover all completed bars returned by the provider. Multi-day downtime leaves explicitly missing sessions; use the upstream B02 backfill pipeline before resuming and audit gaps. No fake empty bars are inserted. An empty provider day reports missing/closed. Real-time mode is an operator assertion requiring an independently verified entitlement and in-session lag check; `delay_unknown` is the honest default. Closed-market health does not prove real-time access, and a recent last aggregate does not confer NBBO access.

Observed through Massive MCP at **2026-10-29 03:34 UTC**: last trade and last NBBO both **NOT_ENTITLED**; aggregate history returned; market closed. Latest returned minute was Oct 28 19:59 ET. Actual in-session aggregate delay remains unknown; prior sessions observed delayed bars. Hosted REST credential entitlement can differ from MCP. Revalidate it on the runtime host; never infer success from subscription wording. [Massive plan information](https://massive.com/pricing).

Implementation status is separate from integration: local executable/tests exist; source is on this draft PR; registry discovery and independent CI are handoffs; main merge, hosted credentials, service startup and observed live health are **not complete**. Dependencies #70/#92/#94 route shared ingestion/traversal; this prototype does not replace their owners. `component.json` is the proposed discovery contract for B00/B06/B08. Discovery: #96; hosted runtime: #97; independent CI: #98. See `HANDOFF.md`.

## Validation

```bash
python -m unittest discover -s research/CRWV/trading-tool/tests -v
```

Tests cover frozen bands, contact debouncing/ambiguity, no-attempt wording, breaks, close traversals, gaps, score/path arithmetic, actual profiles, strict matching, future exclusion, ticker isolation, restart, revisions, rollback, append-only constraints, pagination and mocked polling. They do not establish predictive edge, execution profitability or live-feed entitlement. `VALIDATION.md` preserves observed failures/corrections and corpus evidence.
