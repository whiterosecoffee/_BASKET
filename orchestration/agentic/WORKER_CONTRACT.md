# B00 worker operating contract — MRIE project manager

**Worker:** B00 orchestration/evidence and release governance. **Project:** `whiterosecoffee/_BASKET`.
**This conversation:** issue [#32](https://github.com/whiterosecoffee/_BASKET/issues/32), branch `work/32-mrie-agentic-readiness-audit`, draft [PR #33](https://github.com/whiterosecoffee/_BASKET/pull/33). **Parent orchestrator:** B00 canonical planning and release contract; this is one existing B00 specialization, not a separate orchestrator or task queue. **Version:** contract `basket.worker_task@1` / `basket.worker_resolution@1`, manager decision `basket.agentic_decision@1`, dependency snapshot `basket.dependency_snapshot@1`.

## Ownership and objective

Exclusive permitted writes for #32: `orchestration/agentic/**`, `orchestration/audits/mrie-implementation-readiness-2026-10-17.json`, `orchestration/audits/mrie-dispatch-readiness-2026-10-17.json`. All other files are READ ONLY, even other B00-owned files if another active PR has them. **Explicitly prohibited:** `orchestration/planner/queue.json`, `orchestration/execution_loop.py`, `orchestration/tests/**` (reserved by PR #25); B01 `.github/workflows/**`, `tests/integration/**`; B02 `runtime/**`, `fx/**`, `tickers/*/history.*`, `tickers/*/live/**`; B03 event/filing stores; B04 valuation; B05 relationship edges; B06 traversal; B08 `services/**`, `deployment/**`.

**Purpose:** supply evidence-gated priority decisions, authenticated provenance contracts, collision detection, bounded local validators, append-only attempt/deliverable/lease projections, and deterministic input-revision invalidation to the existing B00 planner. Users and downstream sparks should be able to ask *what is blocked, why, who owns the next step and what immutable proof constitutes acceptance*. Fail closed rather than fabricate implementation or active worker sessions. A draft PR or passing isolated unit tests cannot establish merged/operational status.

## Canonical lifecycle mapping

These are **descriptions**, not new state values. Canonical `WORKER_PROTOCOL.md` remains authoritative.

| Requested description | Canonical persisted state | Evidence required |
|---|---|---|
| Available | no worker claim; queue `ready_new_worker` is a derived projection | live unblocked queue and verified capacity |
| Claimed | `claimed` | own issue, unique branch, `basket.worker_task@1` |
| Implementing | `building` | changes restricted to owned branch |
| Testing | `building` until proven | measured tests, failure attempts and independent QC |
| Review-ready | `review`; `component_verified` only after acceptance | draft PR, exact head SHA, acceptance evidence and CI |
| Integration-blocked | `integration_blocked` | named dependency or conflict with owner and tests |
| Integrated | `integrated` | approved merge and main CI against exact SHA |
| Retired | `closed` or `withdrawn` | B00-verified resolution / disposition; archives do not imply code deletion |

`resume_ready`, `failed_retry_required`, `active`, `blocked`, and `recompute_required` are local **decision labels**; they are never written as new canonical worker-status schema values.

## Inputs / outputs / consumers

- **Authoritative inputs:** current `main` AGENTS.md, `orchestration/sparks.json`, canonical `orchestration/planner/queue.json` and goals, issue claim/comments, all live PR changed paths and head SHAs, exact-head Actions conclusions; B02/B03/B04/B05 source-revision manifests.
- **Versions and time:** `basket.github_evidence@1`, `basket.worker_task@1`, `basket.worker_resolution@1`, `basket.agentic_event@1` (local single-writer projection only), `basket.dependency_snapshot@1`, `basket.dependency_decision@1`. Point-in-time evidence requires the primary `source_url`, `evidence_class`, original ISO currency, conditional `fx_reference`, `effective_at`, `available_at`, `ingested_at`, `valid_until`, SHA256 and revision/version. Foreign-currency requirements block downstream USD model recomputation unless the cited FX revision is present. Expired records remain historical but cannot support current use.
- **Output locations:** draft PR #33 `orchestration/agentic/**` reusable code/tests/contract; original audits in `orchestration/audits/**`; GitHub issue #32 resolution; cross-domain handoffs to B02 issue #11, B08 issue #34, B01 issue #6 and B00 queue owner issue #24 / PR #25.
- **Consumers:** B00 planner and owner action queue; B01 CI/review; B02 data-plane ingestion, B03 issuer evidence, B04/B05/B06 economic graph, valuation and traversal; B08 remote scheduler/API. The new dependency gate reports *intent*, not executed recomputation.
- **Provider dependencies:** GitHub read-only evidence token for live mode; Massive client has historical daily OHLC entitlement as observed, but `last_trade` returned `NOT_ENTITLED`. Hosted credentials, external streaming entitlement and Render runtime are unverified until B08 tests them. No inference of live pricing from a recent fetch timestamp.
- **Errors:** explicit `GuardError`/`DependencyError` with unknown, stale, conflicting, expired, missing-entitlement and missing-source status; never fall back to fixtures in live mode.

## Processing obligation: exact stages

The interface is `Discover → Acquire → Normalize → Verify → Reconcile → Calculate → Persist → Validate → Publish → Invalidate Dependencies`. It is intentionally split among existing owners rather than implemented as a competing monolith:

| Stage | Input to output | Gate and idempotency | Owner |
|---|---|---|---|
| Discover | main queue & registry → owned task and dependencies | queue version + issue ID; reject collisions | B00 |
| Acquire | authorized provider response → raw immutable evidence | provider request id + source revision; fail on entitlement | B02/B03 |
| Normalize | source bytes → source-defined schema and USD/FX metadata | raw SHA, venue, units, precision; reject ambiguity | data owner |
| Verify | normalized value → evidence classification | independent source cross-check / temporal rule | data owner, B01 QC |
| Reconcile | all live PRs, inputs, debts/contracts and owning domain → reconciled manifest | primary record revision and graph contract, no double count | producer + B00 for scope |
| Calculate | validated input revisions → deterministic engine output | model/config SHA and exact input fingerprint | B04/B06/B07 |
| Persist | immutable result/evidence/attempt event → authorized storage | unique source/revision ID; conflict quarantine | domain owner/B08 service |
| Validate | exact PR SHA → unit, adverse/negative, independent QC | no skipped mandatory checks | B01 |
| Publish | approved merged artifact → stable consumption endpoint | exact main SHA/CI, explicit authorization | B00/B08 |
| Invalidate | relevant source revision/expiry → recompute proposal | `dependency_gate.py` source-revision diff and deterministic key | B00 projection; relevant producer executes |

**Retry/checkpoint rules:** source `NOT_ENTITLED` is a blocker, not an exponential retry; 429/5xx may use bounded provider backoff with jitter and Retry-After under B02/B08. On restart, B08 must resume from a durable source watermark, not a chat session. Failed attempts are append-only and retry the *same step* with ancestry; a passing correction must not erase previous failures. Files in this PR use single-writer fsync only; no multi-host lease guarantee until B08 Postgres transactional tests. Unknown active worker count must remain null and must prevent automatic new-worker launch.

## Cross-spark dependency contracts (handoffs, not hidden work)

| Producer → consumer | Version & expected fields | Change trigger; failure & acceptance |
|---|---|---|
| B02 market observations → B04/B06/B09 | existing market-history contract + snapshot manifest: ticker, event/effective/available/ingested timestamps, source/venue/currency/FX, raw SHA, TTD | revised bar/split/FX or expiry invalidates only affected output; 200+ eligible sessions, replay tests; `NOT_ENTITLED` blocks live |
| B03 issuer events → B04/B05/B19 | `events@1`, accession, period, status, source URL/SHA and first availability | correction, funding state or published report triggers linked dependents; missing primary document remains unknown |
| B05 relationships → B04/B09/B19 | `relationships@1`, signed/announced/proposed economic edges and look-through basis | new edge/ownership revision; fail closed on double counting and wrong owner |
| B04/B06 → B08 client | engine algorithm/config version, input manifest SHA and as-of | relevant fingerprint change requires recompute; blocked input emits unknown, no live NAV |
| B00 → B01/B08 | `basket.worker_task@1`, `basket.worker_resolution@1`, project manager contract and source event SHA | owned PR-head/CI changes invalidate acceptance; hosting requires durable leases, protected secrets, remote health and restart proof |

## Quality and failure register

**Implemented locally on candidate branch:** deterministic queue evaluation, cross-PR collision inventory, current-source freshness checks, append-only local attempt/lease/deliverable projections, safe allowlist validations, origin/retry consistency, Massive provider-contract tests, dependency revision fingerprint and invalidation plan. **Independent release status:** pending B01 exact-head CI; not integrated/hosted.

Known failure classes and recovery:
- Old B01 snapshot at commit `5f933c5` found a failed-step requeue mismatch; current PR head has explicit `retry_original_step` branch but requires B01 retest at new SHA.
- PR #25 also changes the canonical planner/loop: preserve its ownership; request queue IDs/acceptance through issue #24 and PR #25 comments.
- Historical Massive daily data is accessible; last-trade is not entitled; no hosted worker credentials verified. Fail closed and use separately labeled historical/delayed observations.
- PR inventories and head CI become stale; refresh immediately before acceptance and every material write. If GitHub API is unavailable, do not use a historical fixture to claim readiness.
- Running a worker or an agent does not itself change inputs; no invalidation without a changed revision/fingerprint.

## Acceptance and prioritized backlog

A1. Formal identity, strict scope, canonical states and versioned I/O contracts in this file.
A2. Regression/negative tests for stale/future source, duplicate revisions, status collisions, same-step retries and fail-closed missing requirements.
A3. `dependency_gate` computes stable source input fingerprints and requests recomputation only when material inputs change; never executes remote work.
A4. GitHub branch contains code/tests/docs and all changed files are B00-owned and disjoint from current PR #25.
A5. B01 independently executes exact-head tests and security/CI at the owning SHA; until then `component_verified` and integrated are NOT claimed.
A6. B02 implements authorized Massive backfill/correction/TTD; B08 deploys authenticated durable runtime; B04/B06 consume pinned source-revision manifests and perform real computation.

Next queue: **P0** repair any independent regression at PR #33 head (B00), **P0** validate B01 CI handoff #6, **P0** B02 source/TTD #11, **P0** B08 hosted runtime #34, **P1** B03 earnings #12, B19 pools #17 and downstream deterministic calibration. Actual launch order must be recomputed from current GitHub state, not this document. Never merge or create dormant branches without authorizing workflow.