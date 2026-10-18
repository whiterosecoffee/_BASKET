# B13 OpenAI private-value worker operating contract (v2 application)

**Ownership authority:** GitHub main `AGENTS.md`, `orchestration/sparks.json` and `orchestration/WORKER_PROTOCOL.md` take precedence over this B13 specialization document. This is a worker runbook and consumer interface, **not a competing orchestration system or schema**.

## 1. Identity and charter

| Contract element | Value |
|---|---|
| Spark | **B13** — OpenAI & Anthropic private-company value research |
| Parent orchestrator | **B00** (exclusive queue, schemas, architecture and release governance) |
| Conversation worker | **B13-26**, issue https://github.com/whiterosecoffee/_BASKET/issues/26 |
| Exclusive branch | `work/26-openai-preipo-valuation-sftby`, opened from main; branch **must not be reused** by a future conversation |
| Draft PR | https://github.com/whiterosecoffee/_BASKET/pull/31 |
| Write paths | `tickers/OPENAI/entity.json`; `research/OPENAI/**` |
| Read-only inputs | `AGENTS.md`, `orchestration/sparks.json`, `orchestration/WORKER_PROTOCOL.md`, `schemas/**`, `architecture/**`, `tickers/OPENAI/events.json`, `tickers/OPENAI/relationships.json`, `tickers/OPENAI/history.jsonl`, `research/SFTBY/**`, `research/filings/**`, `tickers/CRWV/**`, `runtime/**` |
| Prohibited writes | Every other path, particularly `orchestration/**` (B00), `schemas/**` (B00), `tickers/*/history.jsonl` / `runtime/**` (B02), `tickers/*/events.json` (B03), `engines/valuation/**` (B04), `tickers/*/relationships.json` (B05), `research/SFTBY/**` (B09), `engines/narrative/**` (B21), `.github/workflows/**` and `tests/integration/**` (B01) |

**Purpose:** Publish falsifiable, source-dated OpenAI pre-IPO research and conditional economics interface inputs, with clear separation among issuer statements, financing, derivative sentiment, reported run-rates, recognized earnings, hypothetical scenario values and unobserved facts. An internal `OPENAI` entity ID is **not a tradable ticker** and may not receive invented OHLCV. Research contributes to MRIE by defining auditable upstream valuation evidence and targeted change signals without inventing a security, probability, revenue, or SoftBank NAV.

**Success:** Stable source-backed research artifacts with explicit unknowns, strict offline tests, reproducible dependency fingerprints, independent B01 exact-SHA CI, clean owned-path PR and actionable receiver handoffs. **Failure:** hallucinated/current valuation or parent NAV, mutable evidence with untracked corrections, future knowledge contamination, untraceable source claims, unentitled feeds presented as working, unmatched gross/net revenue, erased failure evidence, or cross-spark path edits.

## 2. Interfaces and authoritative data

| Producer → consumer | Version/interface | Required upstream fields | Output / location | Freshness and rejection gate |
|---|---|---|---|---|
| B03 issuer/SEC → B13 | `events@1`, immutable filing ID/accession | issuer ID, source, effective/available/ingested dates, financing lifecycle, signed/funded state | `valuation-register.json`, `ipo2027-news.json` (B13 research copy, **not** canonical event mutation) | Missing announced-vs-funded or first-available date remains provisional; no intraday replay from date-only text |
| B02 market/FX → B13 | B02 snapshot/revision identity per `architecture/VERSIONING.md` | instrument type, venue, original unit/FX, period, mark, source, provider entitlement, as-of and TTD | `resource-registry.json` access inventory and hypothesized sentiment evidence | Expired/stale data never labeled current; derivative oracle is not issuer share price |
| B13 → B04 fundamental economics | `basket.preipo_valuation_research@1`, `basket.openai_ipo_news@1`, `basket.b13_evidence_fingerprint@1` **B13 research-only** | value measure and type, source IDs, available date, currency, unit, recognition basis, evidence class and scenario state | `valuation-register.json`; `evidence_fingerprint.py` emits `consumer_input_hashes.B04` | Missing GAAP/net cash/cap-table => scenario-only or blocked; B04 defines accepted valuation schema and engine |
| B13 → B09 parent NAV | `basket.openai_sftby_interface@1` **B13 proposal** | fund-level rights/ownership, preferred conversion, embedded SVF2 base mark, debt, fees/taxes, FX | `sftby-interface.json`, `consumer_input_hashes.B09` | **Never** add gross 13% to NAV already incorporating SVF2; B09 calculates accepted net parent look-through |
| B13 → B21 claims | `basket.preipo_assumption_register@1`, dated news/revisions | claim, alternatives, falsifiers, source class and dated first availability | `assumption-register.json`; `consumer_input_hashes.B21` | Reported/CoreWeave/Hyperliquid relation is a hypothesis, not verified causality |
| B13 → B00 and B01 QC | `basket.worker_task@1`, `basket.worker_resolution@1` from **existing B00 schema** | issue/branch/PR, immutable source SHA, acceptance, actual CI run, blockers | Issue #26 worker comments, PR #31; not a new queue | B00 independently checks GitHub; B01 workflows test exact immutable B13 revision |

B13 output contracts are **candidate research formats**; B00 #29 must decide shared schema evolution before general downstream production consumption. `evidence_fingerprint.py` performs source-level change analysis only. It does **not** replace B02's journal/checkpoint, B00's queue or B08's runtime.

## 3. Execution process — one owner, explicit evidence

| Stage | Input/authority | Deterministic output and idempotency | Failure / retry / checkpoint |
|---|---|---|---|
| Discover | Live GitHub main + B13 Issue #26 + PR #31 + PR changed-file list | Ownership/scope and requirement snapshot | On path conflict stop that write, hand off exact receiver; continue unrelated owned work |
| Acquire | SEC/issuer/SoftBank transaction, dated reputable reporting and clearly tagged derivative sources | URL, source class, first-available day, period_end and original unit | No entitlement means unavailable; no invented market quote; retry when provider becomes accessible |
| Normalize | Existing `entity@1` and B13 structured research; explicit original currency | USD-first compatible values, separate run-rate vs GAAP, equity vs EV, scenario vs transaction | Reject mixed FX/vintages, common/preferred and gross/net equivalences |
| Verify | Issuer regulatory filing when public, versioned source contents and adverse evidence | Provenance, first-available and typed uncertainty | Contradiction stays disputed and must list falsifier; do not average conflicting claims |
| Reconcile | Company financing rounds, stakeholder share rights, source revision links | Historical revision/supersedes lineage | Preserve immutable prior record and date; competing revisions fail closed |
| Calculate | `ipo2027-policy.json`, user-specified explicit USD scenario | Conditional weights/EV-to-equity scenario; no current value | Missing fundamentals or proposed regime => unrated/blocked, no synthetic probability |
| Persist | B13-owned GitHub branch research JSON/Markdown, no live bars | Source-controlled candidate source snapshots and committed SHAs | Git commit check is a checkpoint; no Git-based high-frequency writer |
| Validate | `check.py`, `ipo2027.py`, `resource_audit.py`, `evidence_fingerprint.py` and adjacent B13 tests | Exact deterministic input hashes and negative test outcomes | Rerun after each material change; do not suppress failures |
| Publish | Draft PR #31 and `basket.worker_resolution@1` GitHub Issue #26 comment | Evidence URLs, exact head SHA and unresolved gates | Passing self-check ≠ independent B01 CI ≠ integrated main |
| Invalidate dependencies | Changed `basket.b13_evidence_fingerprint@1` record and `consumer_input_hashes` | Per-consumer fingerprints and `basket.b13_change_impact@1` **proposal only** | B00/B02/B08 orchestrated scheduling only on validated source/version changes; B13 does not dispatch |

**Idempotency:** source immutable record ID + source revision + available date + contract version; canonical JSON with sorted keys and normalized record ordering. The `dependency_fingerprint` uses SHA-256 of selected records, policy and provider vintages. Identical material input produces identical fingerprint. Reordering source arrays is a no-op. Added evidence triggers only impacted downstream consumer domain hashes. In-place changes to previously recorded evidence are rejected. New revisions use a new ID and `supersedes`, retaining the previous row.

**Important temporal limitation:** Current B13 registers are static 2026-10-17 research vintages, and `ingested_at_utc` is unverified. Therefore `evidence_fingerprint.py` only permits the exact catalog vintage and refuses past/future recomputation claims; a true historical replay requires B02 source-available/ingested timestamps, immutable revision lineage, and stable snapshot manifests. No module pretends a date-only report was knowable intraday.

## 4. Canonical lifecycle mapping

These phrases are explanatory **only**; use the B00-defined states in machine payloads.

| Human phase | Existing `worker_task@1` state | Existing `worker_resolution@1` disposition |
|---|---|---|
| Available (unclaimed) | No issue task claimed; no synthetic task state | No resolution |
| Claimed | `claimed` | `in_progress` |
| Implementing | `building` | `in_progress` |
| Testing | `building` | `in_progress` |
| Review-ready | `review` | `component_verified` or `ready_for_integration`, only with actual proof |
| Integration-blocked | `blocked` or `review` | `integration_blocked` |
| Integrated | `integrated` | `integrated` only after merged, green main checks |
| Retired/archived conversation | `closed` only after B00 issue disposition; alternatively retains `review` | `component_verified`, `integration_blocked` or `withdrawn` as evidenced, not automatically integrated |

B13 does not maintain a second mutable task-status register. Worker task claim and resolution live in GitHub issue comments; accepted schema vocabulary belongs to B00.

## 5. Runbook

From a checked-out PR #31 head:
```bash
python research/OPENAI/check.py --validate --self-test
python research/OPENAI/ipo2027.py --as-of 2026-10-17 --regime neutral
python research/OPENAI/resource_audit.py --as-of 2026-10-17
python research/OPENAI/evidence_fingerprint.py --as-of 2026-10-17
python -m unittest discover -s research/OPENAI -p 'test_*.py' -v
```

`--compare-json path/to/previous_snapshot.json` compares a prior B13 report to the current B13 research snapshot; **do not** place that command's output in `tickers/OPENAI/history.jsonl` or claim it triggered B00 tasks. For a validated planned consumer, include the complete SHA-256, `source commit`, recorded date-vintage and `input IDs` in an owner-specific handoff. Input data is not automatically accurate just because hashes match; hashes prove reproducibility, not truth.

### Failure register / repair policy

| ID | Failure observed or fixture | Resolution/prevention | Verification |
|---|---|---|---|
| B13-F01 | 2026-10-17 valid IPO-stage call raised `KeyError: 'required'` due to eagerly evaluating a blocked-stage message | B13 commit `316dbea...`: check `gate["eligible"]` before accessing `required`. Preserve red B01 run 39094546299 | B01 exact-pinned gate run 39094901748 passed all previous unit and integration tests |
| B13-F02 | Static issuer financials or derivative marks might be promoted as current NAV without class/FX/cash bridge | Hard `net_SFTBY_NAV=None`, scenario flags, preferred rights and SVF2 replacement rule | Existing B13 `check.py` and B01 tests; audited NAV still unavailable |
| B13-F03 | Hypothetical source revisions overwritten at same ID or future-available reporting enters as-of sample | `evidence_fingerprint.py` new ID/`supersedes` policy, as-of input rejection and deterministic consumer hashes | B13 `test_evidence_fingerprint.py`, pending independent B01 run at new commit |
| B13-F04 | Massive public financials returned NOT_ENTITLED; SEC XBRL year-to-date/quarter confusion | Explicit provider state, SEC filing fallback and period comparison; no automatic economic import | `resource_audit.py`, source registry; no scheduled adapter deployed |
| B13-F05 | Branch created before recently merged shared QC policy (main advanced) | Keep PR on isolated branch; B00 coordinates refreshed merge-base/compatibility review, no cross-owner edits | GitHub diff/collision check against current main required before integration |
| B13-F06 | 2026-10-18 dedicated OpenAI gate ran **all 32 B13 unit tests successfully** but returned red when the independent B01 test path was absent in an older B13 branch checkout (exit 5) | Existing B01 successor issue #64 must checkout independent B01 acceptance tests from a compatible exact ref, fail if empty and rerun exact source SHA; B13 must **not** edit workflow | Red run https://github.com/whiterosecoffee/_BASKET/actions/runs/39097427403 preserved; issue #64 receiver comment 6245697240; overall gate pending |

Retry rule: same source ID + unchanged digest does not reprocess. Retry transient provider failures only under owner-operated B02/B03 infrastructure; B13 re-runs only after new source/version availability. If new record has contradictory values, annotate explicit alternative and retain both; do not overwrite or hide the old value. Record failed CI run and corrective commit separately.

## 6. Acceptance matrix and ranked next work

| Criterion | Present status | Gate / receiver |
|---|---|---|
| B13 private issuer classification and SEC/issuer sources | Implemented as research | B00 audit PR #31 |
| B13 dated news, valuations, claims and SFTBY gross-only interface | Implemented as research | B00 #29 and B09 #28 for shared downstream contract |
| B13 stage/regime weights and no-lookahead/unknown gates | Independently validated for older SHA `316dbea...` | B01 #64 must test **new PR head** after revision/fingerprint extension |
| B13 deterministic revision fingerprint + consumer invalidation | Implemented in B13 branch; negative fixtures checked in | B01 #64 independent exact-SHA CI pending |
| Provider rights and persistent time-stamped ingestion | NOT implemented by B13 | B02 #11, B03 #12, B08 #34/#53 |
| GAAP-normalized private issuer FCFF/EV-to-equity and calibration | NOT implemented | B04 #30, B00 #29 |
| SFTBY fund NAV embedded mark, fees/debt/FX reconciled | NOT implemented | B05 #16 and B09 #28 |
| B00 queue/integration and main release gates | NOT decided by B13 | B00 #36, active queue PR #25; explicit user merge authorization |

**Highest next B13 action** when external validators integrate: refine revision impact with B02 canonical `snapshot_sha256` and immutable available/ingested times after contract #29 lands, then move source selectors from fixed 2026-10-17 research vintage to point-in-time replay. Do not expand into B04 models or B00 orchestration. Do not create unused providers, schedulers or new worker branches.

**Exit/retirement:** This conversation can be archived when the exact-PR-head result, code/test failures, updated resolution, handoffs and next B00 action are durably posted. Draft PR and dependency issues may remain open for owning reviewers. Archive does not imply merge, release, live feed, or current OpenAI equity mark.
