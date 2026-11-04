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

## Reconciliation with existing B02 work (checked 2026-11-04 against GitHub; main b491012)
Earlier versions of this record and issue #151 did not link these; that was an omission.
| Existing item | What it says | Relation | Disposition |
|---|---|---|---|
| #61 comment 6540224140 (user-directed P0 dispatch, "awaiting owner claim") | B02 minute-data ingestion; candidate new path `runtime/minute_ingest/**`; reuse observation identities, replay, TTD, FX; no continuous ticks in Git history; publish a minimal read-only minute/volume/FX contract for B06 #108 and #128 | This work is a design-phase answer to it. Our path is `runtime/fetch/**`, not the candidate path. | Extend. B00 or the owner to arbitrate the path; rename is cheap before code exists. Not yet a formal claim. |
| #62 workers MW02 (session clock, holidays), MW04 (pilot 1-minute repair, pagination), MW06 (timestamp normalization, corrections) | Planned B02 workers with exact scopes | Overlap in intent with calendar, paging and revision handling | Consolidate: reuse their acceptance wording; do not build a second calendar. |
| #11 / PR #15; merged #140 (`runtime/observations.py`, `runtime/ticker_data.py`, NVDA-only) | Observation identities, revision and replay; connector CSV parsing and fingerprinting for NVDA | Reusable vocabulary (record identity, supersedes, expected head). `ticker_data.py` is NVDA-only and single-journal | Reuse naming and revision semantics; do not import the NVDA store. Block files stay separate. |
| #61 comments 2026-10-29 | GitHub is canonical for daily JSONL; GitHub is not a high-frequency tick store; live tick collection is a separate runtime concern | Policy tension with minute blocks in the public repo | Owner decided an ORCL-first pilot of settled-session blocks (not ticks). Keep that decision; storage trigger below. |
| #148 / #173 NVDA frozen-source resolver pilot (`orchestration/nvda_pilot/**`) | Resolver pilot on main, NVDA-first | R5 is partly answered for NVDA only | Re-read before targeting any resolver; not verified here for ORCL. |
| B06 requests on #152 (comments 6621039200, 6621339893) | Source-quality packet for CRWV/ORCL 1m, 2026-10-01..11-04: source/entitlement, IDs/hash, availability, basis, bar-start vs completion, NY calendar, coverage counts and gaps, policies | Blocking for B06 M1. Inventory only; no broad fetch | Obligation on B02; see "Source-quality answer" below. |

## Source-quality answer (what is verified, what is not)
Verified in this work: minute aggregates for ORCL were returned by the Massive connector for 2026-10-30 (`adjusted=false`); `t` is the bar **start** (connector field key); one session shows 390 bars in 09:30-16:00 ET, 70.4% fractional volume, 24.5% `vw` outside `[l,h]`. Policy in this design: keep fractional volume exactly; flag `vw` per block, never clamp or fill; accept bar starts 04:00-20:00 ET only.
Not verified: approved-source status of the connector for canonical use, snapshot or source IDs, point-in-time availability and revisions, bar-completion time, auction and correction treatment, notional definition, coverage over 2026-10-01..11-04, exact gaps. These remain **SOURCE_QUALITY_AMBIGUOUS / unknown**. The single-session measurement is not canonical coverage.

## Connector-to-code route (R7 probe, 2026-11-04)
- `MASSIVE_API_KEY` is **not set** in this environment, so direct REST is unavailable here.
- The connector exposes `search_endpoints`, `call_api`, `query_data` and `workspace` (create, list, delete). None exports rows to a file. In this environment rows can reach the repo only if a model emits them, which is the transcription risk.
- Mitigation (design hypothesis, **untested**): before staging, compute per-session aggregates in the connector workspace by SQL (row count, `sum(t)`, `sum(o)`, `sum(h)`, `sum(l)`, `sum(c)`, `sum(v)`, `sum(n)`, `sum(t*v)`) and require the staged file to reproduce them exactly after parsing; any mismatch rejects the block. Aggregates are necessary, not sufficient (compensating swaps could pass); the sum of `t*v` and ordered sampling reduce but do not remove that risk.
- A key-bearing host process (an option in the table above) removes the issue and remains the cleaner route when available.

## Worker home and layering
Rationale (from the contract, not preference): `orchestration/agentic/massive_worker_contract.py` `validate_specs` accepts B02 writes only under `runtime/` and `fx/`, so a top-level `_FetchMassiveData/` would fail until B00 changes the contract.
Three layers that change independently: (1) generic fetch pattern (`runtime/fetch/`: plan, fetch, sanitize, stage, verify, promote, manifest); (2) Massive adapter, runbook and training (`runtime/fetch/massive/`); (3) data roots, configurable and resolver-driven (intake under `runtime/fetch/intake/`, permanent home under `tickers/<T>/intraday/` or whatever the resolver names). A second provider is then a new adapter, and a path move is configuration. The worker identifier `_FetchMassiveData` would be registered in B00's worker catalog. Package names are lower-case by convention only; underscore-prefixed or capitalised names import correctly (an earlier chat remark that they "cause import problems" was wrong).

## Hypotheses and reuse recorded, not adopted
- **Settlement lag.** "Session date earlier than today ET" is a conservative design choice. Two same-day pulls differed (893 vs 898 rows); how long counts keep changing was never measured. Trigger to revisit: compare repeated pulls of the same session over several days.
- **Early closes.** A small static table of known early-close dates, labelled unverified against the exchange calendar, would let the worker flag without claiming gaps. Not built.
- **Mixed bases in one folder.** `tickers/SFTBY/intraday/` holds 5m files with `adjusted: true`; the 1m blocks are unadjusted. Readers must check the basis recorded in the manifest. A directory listing alone does not state it.
- **Optional.** A cited verification pass on the prior-art families; hash-chaining manifest records.
- **Continuity hold, mechanism.** Before accepting session N, refetch the final bar of the prior stored session and compare its close with the stored close (exact equality expected for unadjusted data). Mismatch: write nothing, record `hold`. A mismatch whose ratio is near an integer or its inverse is labelled split-like; otherwise revision-like; the label only steers which resolution option is tried (wait, refetch, escalate), it does not decide. If no refetch is possible, record `continuity_unchecked` and do not promote. The thresholds are unmeasured and not set here.
- **Redistribution premise.** The owner decided minute data may be committed to the public repo as an ORCL-first pilot. This work did not check the provider's redistribution terms (the SpotGamma intake on PR #125 raised the same question for another vendor). Owner or B00 to confirm; this is not a reopening of the decision.
- **Ticker allowlist.** Whether the pilot enforces an ORCL-only allowlist in configuration (recommended in discussion) or relies on convention was not decided. Unresolved.
- **Storage trigger.** About 60 KB per liquid ticker-session (one session, hand-counted rows); revisit git as the store before more than a pilot set of tickers.

## Open items (owner and routing in the B00 handoff issue)
ORCL ticker home; worker registration; optional `market.intraday.1m@1` schema; intraday check in the shared validator; path resolver (#148); continuous operation feature request; connector-to-code fidelity route.
