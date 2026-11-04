# Massive 1-minute fetch pattern — architecture record

Spark B02 | issue #151 | status: **design record, no code**. Nothing here is a running worker, live feed or entitlement claim.

## Decisions already made (by the project owner; not reopened here)
- One immutable file per ticker per completed ET session: `tickers/<T>/intraday/<YYYY-MM-DD>.1m.jsonl`, plus append-only `tickers/<T>/intraday/manifest.1m.jsonl`.
- 8-field rows `[t,o,h,l,c,v,vw,n]`; unadjusted (`adjusted=false`), basis recorded; no CSV is stored at any stage.
- ORCL-first pilot; minute data may be committed to the public repo.
- Staged flow: **intake -> verify -> promote**. Intake lives git-tracked under `runtime/fetch/intake/<T>/`; promotion into `tickers/<T>/intraday/` is a separate draft PR the owner authorizes.
- Continuous operation is a feature request, not part of this work (depends on the NVDA spark being online).

## Fixed procedure vs runtime option sets
Rule: **specify what protects truth, ownership or irreversibility; offer options for what only affects efficiency or order.** Every run records the option it chose and the criteria values it saw.

### Fixed (fail-closed, tested)
| Area | Rule |
|---|---|
| Row/file/manifest format | as decided above; manifest record carries `fetched_at`, `sha256`, row count, status |
| Sanitize | dedupe `t`; drop non-finite or <=0 prices, `v<=0`, `n<1`, OHLC violations, off-minute `t`; accept only 04:00-20:00 ET bar starts; every drop logged with reason |
| Never | forward-fill, int-cast volume, reject a bar for `vw` outside `[l,h]` (flag only), drop `o=h=l=c` bars that have volume |
| Settled sessions only | session ET date earlier than today's ET date |
| Conflicts | a differing re-pull is a `conflict` plus a new revision record; never overwrite |
| Holidays / early closes | 0 results = status `no_bars` (not a gap); early closes flagged, no gap claim |
| Continuity hold | compare prior stored close with a refetch before accepting a new session; mismatch = `hold`, nothing written |
| Promotion | needs verification evidence, a target ticker home that passes `tests/validate_stores.py`, and an owner-authorized PR |
| Security / governance | key only from `MASSIVE_API_KEY`; no merge; B02 write paths only |

### Runtime option sets (worker chooses and records why)
| Choice | Options | Criteria |
|---|---|---|
| Acquisition route | connector tool, REST with key, host-side script | key present; entitlement known; output reaches code without model transcription |
| Session order | oldest-first, newest-first, gaps-first | watermark state |
| Batching | one session per call, multi-day window, parallel tickers | rate limits, 50,000-row cap, proxy concurrency |
| Verification depth | single pull, double pull, double pull + independent source | cost vs risk; raise after a hold or on early-close days |
| Promotion cadence | per session, per week, per month | review load |
| Hold resolution | wait, refetch, escalate to owner | split-like vs revision-like mismatch |
| Storage backend | git, columnar, external store | measured size (see below), not guessed |

An option that shows a clear winner after several *measured* runs may be promoted to the fixed list. Until then it is a hypothesis.

## Measured evidence: one ORCL session (read-only)
Source: Massive connector, `/v2/aggs/ticker/ORCL/range/1/minute/2026-10-30/2026-10-30`, `adjusted=false`, `sort=asc`, `limit=50000`, stored as table `orcl_1030` and queried with SQL in the connector workspace. A single session; **not** a statistical sample. No market rows are committed.

| Query result | Value |
|---|---|
| rows / distinct `t` | 824 / 824 |
| off-minute `t` | 0 |
| `v<=0`, `n<1`, OHLC violations | 0, 0, 0 |
| bar-start range (ET, fixed UTC-4 offset, valid because DST ended 2026-11-01) | 04:00 .. 19:59 |
| rows with bar start 09:30 <= t < 16:00 ET | **390** |
| fractional `v` | **580 of 824 (70.4%)** |
| `vw` outside `[l,h]` | **202 of 824 (24.5%)** |
| flat bars (`o=h=l=c`, with volume) | 134 of 824 (16.3%) |

Consequences for the design:
- Fractional volume is the norm; an int-cast would corrupt most rows. This confirms the fixed rule.
- `vw` outside `[l,h]` is common, not an edge case, so "flag, never reject" must be cheap and must not flood the manifest: **record per-block counts, not one line per bar** (design change from the pre-measurement plan).
- Flat bars are common and legitimate; keep.
- The module must use `zoneinfo` America/New_York, not the fixed offset used for this one query.
- Size: the connector reports 72.4 KB uncompressed for the in-memory table (with a ticker column). By hand-counting the five preview rows, a JSONL row is about 73 bytes, so this block is **roughly 60 KB** (estimate, not a written file). At 252 sessions that is about 15 MB per ticker-year for a liquid name; widening beyond a pilot needs a measured storage decision. This replaces the earlier 40 KB guess.

## Prior art (design vocabulary; unverified recall)
No source was fetched for these. Treat as vocabulary, not evidence.
Write-Audit-Publish / staged promotion; append-only ledger with revision records; bitemporal data; content addressing (hashes, optional hash-chained manifest); Singer/Airbyte-style connector with a state bookmark (here the manifest watermark); declarative data-contract checks; tickplant-to-end-of-day store; trade-based bars; raw plus separate adjustment; idempotent natural-key writes; agent runbooks. Repo precedent that *is* verified: `runtime/ticker_data.py` (ports/adapters, idempotent, atomic replace, explicit `no_data`), and `architecture/BLOCK_ENGINEERING_METHOD.md` (Design by Contract, ports/adapters; "not a novel framework").

## Open items (owner and routing in the B00 handoff issue)
ORCL ticker home; worker registration; optional `market.intraday.1m@1` schema; intraday check in the shared validator; path resolver (#148); continuous operation feature request; connector-to-code fidelity route.
