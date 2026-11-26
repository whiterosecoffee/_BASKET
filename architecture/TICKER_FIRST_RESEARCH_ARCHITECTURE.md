# MRIE Ticker-First Research Architecture — Proposed Contract

Status: design proposal, NOT implemented migration or released schema. Owner: B00. Issue: #42. Branch: work/42-ticker-first-worker-contract.

## Architectural invariants
1. A ticker/entity is the canonical home of its observations, active ranges, market/operating regimes, earnings, contracts, revenue exposure, valuations, hypotheses, evidence provenance and processing checkpoints. Shared aggregates may reference ticker facts but must not create competing canonical copies.
2. Shared infrastructure owns reusable schemas, algorithms, templates, provider adapters, worker scheduling, identity and quality controls. Cross-entity aggregates contain only genuinely multi-entity reconciliations, graphs, basket risk and capital-flow totals.
3. **Logical organization is not immediate filesystem authority.** Preserve existing B02 tickers/*/history.jsonl, B03 tickers/*/events.json, B05 tickers/*/relationships.json, B04 engines/valuation, and company-specific research/<ticker>/** contracts until owner-approved, tested migration. Never silently move files or broaden spark write_paths.
4. Raw observations and evidence are append-only, with revisions and supersession; derived current views are reproducible projections. Record effective_at, period_end, first_available_at, observed_at, ingested_at, calculated_at (when relevant), source identity, model version, and USD conversion provenance. Missing dates are null, not guessed.
5. Explicit evidence classification: verified_observation, company_statement, inference, scenario, unknown_or_conflicted. Never treat forecasts, relationships or private-market marks as realized revenues or executable quotes.
6. Relationship edges have stable identity, source provenance, validity window, evidence status, counterparty perspectives and directed economic roles. Each ticker owns its perspective; aggregate graph deduplicates shared edge identity. Separate end-customer spending, intermediary revenue, supplier sales, value added, capital spending and financing to prevent double counting.
7. Regimes are multidimensional, with domain, measurement window, observed evidence, classification method, confidence/calibration, invalidation criteria and model version. Active ranges are ticker-level derived records with boundaries, window, method, as-of timestamp and freshness.
8. Point-in-time reconstruction must never use information first published after the simulated decision timestamp.

## Logical entity domains (not immediate rename instructions)
- observations: market/history, issuer filings, statements, earnings, estimates, contracts, issuer claims, sources.
- analysis: active_range, regimes, financial/economic interpretation, revenue pools, valuation scenarios and assumptions.
- relationships: ticker-specific counterparty perspective and shared relationship IDs.
- thesis: hypotheses, causal pathways, catalysts, falsifiers, unresolved evidence.
- state: coverage, source watermarks, last verified input IDs, run/version fingerprints, retries and gaps.

Canonical ticker-root paths remain unchanged pending explicit B00 schema and owner migrations. A logical domain may be implemented as research/<ticker>/** where that company worker already has exclusive ownership.

## Reusable worker contract
A task identifies schema version, stable task ID, ticker/entity ID, worker capability, recipe/template version, parameters, provider capability requirements, authorized write paths, source watermarks, dependencies, expected output schema, acceptance tests and idempotency key. Use existing basket.worker_task@1 / basket.worker_resolution@1; any additional task-schema fields require separate B00 schema version review.

Workers are ticker-agnostic executors, composed from discovery, fetch, normalize, verify, reconcile, calculate, persist and impact-propagation capabilities. They do not obtain write authority from a template or provider. Store run attempts, failure class, retry lineage and QC evidence separately from economic observations. Do not assume GitHub/ChatGPT is a continuously running ingestion service.

Provider adapters are capability-based and entitlement-aware: Massive market/financials/SEC endpoints where available; SEC EDGAR and issuer IR for authoritative verification; provider-specific timestamps, identifiers, pagination, rate limits, currency and coverage retained. Never claim an endpoint or entitlement is live without an actual successful call. Missing data is an explicit gap, not a zero.

## Incremental dependency pipeline
1. Discovery detects new source accession/filing/market-data revision and creates a deterministic source identity.
2. Fetch/extract and cross-source reconcile; invalid records quarantine with reason.
3. Persist only schema-valid, provenance-backed ticker observations through authorized owner.
4. Recompute affected ticker-level financial, regime, active-range and valuation projections using versioned input fingerprints.
5. Propagate only verified affected relationship IDs to counterparties via handoffs/owner workers.
6. Recompute aggregate capital flows, pool totals and portfolio analytics from referenced ticker revisions.
7. Record QC result, watermark, coverage gap and next dependent task. Worker completion does not imply research completeness.

Deduplication keys include entity, source document/accession, fact taxonomy, fiscal period, units, effective date and revision identity as applicable. Reprocessing must be idempotent; corrections preserve prior versions.

## Migration / integration gates
M0 inventory existing canonical paths, schemas, GitHub PR overlaps and /MRIE Library artifacts. Preserve stable IDs and create source-to-destination mapping.
M1 publish B00 versioned domain and task schema proposals; keep compatibility readers; review with B02/B03/B04/B05/B19 and B01.
M2 implement one provider adapter and a single ticker-agnostic earnings workflow on an owner-approved disjoint path; compare MU, NVDA and CRWV using the same worker code.
M3 replay point-in-time and duplicate-ingestion fixtures; test conflicting source values, FX dates, filing amendments, provider outages and partial failures.
M4 migrate one ticker's views with byte/record counts, hashes, cross-references and rollback; do not delete originals until verified.
M5 scale to full registry; detect coverage holes and prioritize underrepresented entities without altering canonical membership implicitly.
M6 introduce durable scheduler/leases and hosted data plane, with bounded retries, health checks, cost controls and entitlement verification. GitHub PRs remain review-gated.

## Ownership and immediate handoffs
- B00: approve logical/canonical mapping, schema changes, planner templates and task protocol; avoid queue.json collision with #24 / PR #25 and #36.
- B01: independent validation and CI tests after contract versioning.
- B02: market bars, active ranges, regime input freshness and market-history ownership.
- B03: filings/events canonical ledger, issuer accessions and revision history.
- B04: valuation model contracts and input fingerprinting.
- B05: stable relationship IDs, edge semantics and migration.
- B19: revenue-pool attribution, intermediary pass-through and aggregate reconciliation.
- Company workers: company-specific research under existing authorized research/<ticker>/**.
No receiver work is considered launched until the owning issue/branch actually claims it.

## Acceptance for this design-only PR
A1 documented ticker-vs-aggregate ownership; A2 bitemporal/provenance and immutable revision semantics; A3 ticker-independent worker/provider contract; A4 lossless staged migration and owner handoffs; A5 disjoint single-file PR. This proposal does NOT claim operational workers, updated queue, validated runtime, completed ticker coverage or a released architecture version.

## Compatibility matrix and first executable pilot

| Domain | Current authoritative path / owner | Future logical home | Migration rule |
|---|---|---|---|
| Daily price and volume | tickers/<T>/history.jsonl, B02 | ticker observations/market | Keep path and append-only history until B02 compatibility and replay pass |
| Issuer events | tickers/<T>/events.json, B03 | ticker observations/events | Preserve accession and event identity; B03 alone writes |
| Counterparty edges | tickers/<T>/relationships.json, B05 | ticker relationships | Stable edge ID, cross-perspective references; B05 alone writes |
| Company evidence | research/<T>/**, entity spark | ticker observations/analysis/thesis | Logical projection first; company spark controls its research files |
| Valuation engine | engines/valuation/**, B04 | shared reusable computation | Code remains shared; per-ticker inputs/results live in ticker-owned research projections |
| Supply-chain themes | research/themes/supply-chain/**, B19 | aggregate reconciliation | Only multi-company pools and reconciled flow totals are aggregate; ticker allocations reference canonical ticker facts |
| Worker catalog and queue | orchestration/planner/**, B00 | shared control plane | Do not touch until #24/PR #25 ownership collision is cleared |

### Worker task compilation (illustrative; not a replacement for basket.worker_task@1)

A B00 planner compiles an existing versioned worker issue task plus a capability-specific payload. The example below is **not** a currently registered or executed task:

```json
{
  "ticker": "MU",
  "capability": "issuer_earnings_extract",
  "template_id": "quarterly_issuer_reconciliation",
  "template_version": "1.0.0-proposed",
  "provider_preferences": ["massive", "sec_edgar", "issuer_ir"],
  "period_selector": "latest_unprocessed",
  "required_evidence": ["source_document", "accession_or_issuer_document_id", "first_available_at"],
  "idempotency_dimensions": ["ticker", "document_id", "period_end", "fact_key", "revision"],
  "output_owner": "B03",
  "write_paths": ["tickers/MU/events.json"],
  "downstream_notifications": ["B04", "B05", "B19"],
  "required_checks": ["schema", "provenance", "replay", "no_duplicate"]
}
```

This compiled payload does not grant permission to modify MU's research files or B03 records from another spark. It routes the task to the authorized owner. A production template must validate against a newly approved versioned schema.

### Pilot acceptance cases

1. **Same code, different ticker:** MU, NVDA and CRWV use identical worker code; only configuration and discovered issuer data differ.
2. **Repeat:** processing the same accession and facts twice yields no duplicate canonical observations.
3. **Amendment:** amended filing preserves original records and creates a linked revision, not a silent overwrite.
4. **Point-in-time:** replay before publication excludes the later-disclosed fact even if its economic effective date is earlier.
5. **Missing provider entitlement:** Massive denial or unsupported endpoint records a coverage gap; SEC/IR fallback is attempted where lawful and available, without fabricating a value.
6. **Currency:** USD display values retain original denomination and dated FX conversion provenance.
7. **Ownership:** worker cannot write outside assigned spark paths, even if a template requests it.
8. **Recalculation:** only models whose input fingerprints changed are invalidated; aggregate outputs reference exact ticker record revisions.
9. **Crash/retry:** a failed run can restart from its checkpoint and retains the failed-attempt evidence.
10. **Revenue flow:** multi-hop supplier payments reconcile without counting pass-through revenue as additional final-customer spend.

### Concrete dispatch prerequisite

The planner may add a ticker-by-capability coverage matrix and task generation **only after** the active B00 queue PR #25 resolves its write collision. First worker implementation belongs to an owner-approved domain path; B01 independently validates. Until then, this PR is a reviewed architecture proposal, not proof of running automation.

## Integration review addendum — canonical registry and single-runtime boundary

Read-only GitHub review found that `tickers/MU/entity.json` and `tickers/NVDA/entity.json` are **not present on current main** (GitHub contents API returned 404). This is not evidence that these companies are absent from research datasets: ticker research universe and canonical admitted registry are distinct. Before claiming full-basket coverage or executing the #48 CLI against `tickers/`, B00 must verify the actual canonical entity registry, its identity schema and the complete admitted entity set. An empty or partial `tickers/` tree is not equivalent to the entire research basket.

The #48 dispatch compiler consumes `entity.json` directories and emits offline coverage proposals; it is **not** a provider adapter, canonical writer, scheduler or verified full-basket inventory. Its capability ownership is a proposed routing table and must be reconciled with spark write_paths (notably B03 vs B05 and company researchers). The research-universe comparison documented by #48 reports 68 research IDs in B19 PR #18 and 42 candidates in PR #23, with no overlap, i.e. 110 distinct *research* IDs; this is not proof of 110 admitted canonical entities. Reconcile the lists and entity types before dispatch.

PR #33 owns `orchestration/agentic/**` and must remain the single task/lease/attempt manager. PR #25 owns the queue; PR #47 owns independent QC; #48 owns only `orchestration/capture_dispatch/**`. Any implementation should connect the #48 proposal output into the existing agentic manager through a versioned, validated interface rather than implementing a second scheduler, task queue or attempt ledger.

**Additional pre-pilot gates:**
- G0: demonstrate a complete, validated canonical registry with provenance and explicit research-universe omissions; otherwise fail closed.
- G1: map each proposed ticker-capability task to an existing authorized spark and exact path, or leave it blocked for contract arbitration.
- G2: prove one idempotent, point-in-time source→ticker observation→checkpoint cycle, with no unverified `fresh` status based solely on user-supplied coverage JSON.
- G3: demonstrate the manager/dispatch interface on a fixed fixture and independent B01 checks before scheduling real provider work.
- G4: report live execution only after real authenticated provider evidence, durable persistence and restart tests.

## Conversation synthesis: persistent execution and research-completeness contract

The source conversation established **separate** success dimensions: (1) code/worker delivery, (2) verified source coverage, (3) model and economic interpretation, and (4) autonomous operating readiness. No one dimension substitutes for another. A completed dispatch or green CI run must not imply complete research, live data, a calibrated valuation or persistent hosting.

### Coverage unit and scorecard

Track each admitted `entity_id × capability × fiscal_or_market_period × evidence_class`. For each cell retain: owner, required source types, verified source IDs and revision IDs, earliest availability, last observation, data freshness policy, status (missing/blocked/unverified/stale/fresh/conflicted/not_applicable), last successful run and exact validation SHA, outstanding uncertainty, next action, and dependent outputs. A cell may be `fresh` for a known fact while research remains `partial` because other required sources are unavailable. Unknown evidence must never be converted to zero. Research candidates remain separately tracked until admission.

An aggregate dashboard reports admitted entities, candidates, coverage numerator/denominator by capability and period, blocked gaps by cause, provenance validity, retries and stale cells. Exclude `not_applicable` from relevant denominators but preserve the classification reason. Prioritize neglected entities as well as headline tickers; never substitute a six-ticker fixture for the full registry.

### Reusable task and dependency fingerprint

A task proposal is not a worker claim. The existing B00 manager should translate validated proposals into owner-scoped `basket.worker_task@1` issues/leases. Task fingerprint: entity ID, capability, period, source-revision set, recipe version and model version. Worker writes only authorized canonical records, then emits a completion event containing immutable input/output IDs, checks, run identity, provider evidence, timestamp and changed dependency fingerprints. The manager schedules downstream work **only if** the relevant input fingerprint changed. Duplicate events and retries are idempotent. Unmet source/permission gates become explicit blocked tasks, not silent successes.

Example dependency fanout: new issuer filing → B03 source ledger and earnings revision → company interpretation + B04 valuation input recalculation + B05 relationship candidate assessment (only if filing contains relationship evidence) → B19 aggregate revenue-pool reconciliation → B21 thesis/signal invalidation. Market price update → B02 history/freshness → active-range and regime projections → affected B04/B06 valuation/traversal. Cross-support claims remain hypotheses until separately evidenced.

### Economic attribution and falsification

At every supply-chain depth distinguish payer, customer, contractual counterparty, distributor/intermediary, recognized revenue, gross profit retained, financing, capex, and ultimate end-demand. Shared pool totals must reconcile multi-hop flows rather than sum every company's recognized revenue as independent final demand. Distinguish booked revenue, contracted backlog, capacity options, management forecasts and scenario estimates. Store negative evidence and falsifiers alongside bullish cases. Contracts need source, dates, units, exclusivity/termination where evidenced, and confidence classification. Inference may inform scenarios but cannot silently become a verified edge.

### Acceptance progression

- C0: canonical registry reconciled against research/candidate universes, with omissions and entity type reasons.
- C1: validated dispatch/manager interface, strict owner paths, stable task fingerprints and no duplicate scheduler.
- C2: real source acquisition, immutable ticker observation, first-available timestamp and duplicate-safe amendment/replay.
- C3: evidence-linked derived ticker analysis (earnings, active range/regime, capacity, valuation or thesis), with a reproducible dependency fingerprint and falsifiers.
- C4: durable scheduled execution and restart recovery, verified provider entitlement and measured freshness.
- C5: complete admitted-universe coverage report by capability/period; every gap explicit and prioritized.
- C6: cross-ticker capital-flow and revenue-pool reconciliation without double counting, with source-linked relationships.
- C7: continuous QC: failure classification, retry lineage, regression tests, drift/coverage alerts, resource and latency measurements, and independent head-SHA verification.

C0–C3 are a pilot milestone; C4–C7 establish ongoing operation. The first pilot must use the same worker implementation for MU/NVDA/CRWV, but all admitted entities must be inventoried before pilot results are promoted as representative.

### Retirement and ownership

Chat retirement transfers **the executable requirement and its acceptance evidence**, not just a summary. The B00 orchestrator must record: source issue/PR/SHA, actual owned files, live blockers, receiving owner and issue, explicit acceptance gate, tests not run, and ONE next unblocked action. Existing #48 dispatcher, #33 manager, #25 queue, #47 QC, B02/B03 stores, B08 runtime and B19/B04/B05/B21 downstream owners must be reused. Never invent a new owner or edit an occupied file to accelerate the handoff. 

## Autonomous worker execution and conflict-free retirement protocol

This is a proposed operational contract for existing spark workers; it does not override AGENTS.md, WORKER_PROTOCOL.md, active PR ownership, or merge permissions.

### Before editing

1. Refresh main AGENTS.md, orchestration/sparks.json, WORKER_PROTOCOL.md, current task issue, base branch and relevant open PR changed paths. A GitHub issue is not evidence that a chat session is currently active.
2. Declare **exclusive writable paths** and read-only dependencies. If another PR touches a proposed writable path, stop editing that path; work on disjoint deliverables and issue a precise handoff.
3. Reuse an existing owner issue/branch where legitimately claimed. Otherwise create a unique issue and main-based branch under the documented governance; never reuse another conversation's branch.
4. Convert the assigned objective into concrete acceptance checks and negative tests before implementation. Do not expand scope just because another worker is delayed.

### Maximize independent progress

Implement, validate, and commit all work inside the claimed paths that does not require an external decision. Inspect interfaces read-only; use mocks/fixtures where live credentials or another owner's implementation is unavailable. Run local tests, independent static checks, schema checks and exact-head CI where available. Capture failure classes, reproducible commands and remediation attempts. Never count a skipped/missing test as passing.

When blocked, split the task into (a) work that can still proceed independently and (b) the minimal cross-owner dependency. Continue (a), open or update a handoff issue for (b), and do not mutate the receiver's files. A handoff should be actionable without rereading the originating conversation.

### Handoff payload (required fields)

- source spark, issue, branch, PR, exact commit SHA and changed paths;
- receiver spark, existing receiving issue/PR if any, exact owned path and required interface;
- status: implemented/tested/proposed/blocked, with unexecuted checks explicitly named;
- input and output contract, sample fixture and source/provenance requirements;
- dependency gate, reproducible validation command and acceptance criteria;
- conflicts checked (PR changed paths and time of inspection), known blockers and next unblocked action;
- consequences of inaction and safe fallback; no claims of running workers without evidence.

### Terminal worker response and orchestrator intake

Worker response is a **resolution record**, not an invitation for routine user approval: exact PR/commit, scope and tests, incomplete coverage, open dependencies, next owner and smallest next executable step. The orchestrator verifies changed files and current heads, deduplicates handoffs by capability/entity/period/dependency, assigns existing workers within active limits, and updates planner only through its owning branch. A retired conversation's issue/PR stays open until independently integrated; chat archival does not imply closure.

### Acceptance / collision stress tests

- Two workers request same file: one owner proceeds; the other switches to read-only plus handoff.
- Dependency missing: worker finishes all fixture-driven independent work and records a blocked integration gate.
- Another PR advances: recheck current head before rebasing, CI conclusions or handoff closure.
- Test not executed or provider unauthorized: mark unverified, never successful.
- Repeated handoff: update existing receiver issue rather than creating duplicate tasks.
- Worker crashes mid-run: issue/branch/commit and checkpoint evidence allow restart without relying on chat memory.
- User absent: continue authorized steps until genuine external permission/credentials/governance boundary.

## B00 #42 worker operating contract — reconciled with main governance

**Identity:** Spark B00 (architecture/contracts), issue #42, branch `work/42-ticker-first-worker-contract`, draft PR #43, parent B00 orchestrator. This conversation's **exclusive write** is this architecture file only; the spark's broader `architecture/**` permission does not expand this issue's scope. Other paths, including `AGENTS.md`, `orchestration/WORKER_PROTOCOL.md`, `orchestration/planner/**`, `orchestration/agentic/**`, `orchestration/capture_dispatch/**`, `schemas/**`, `tickers/**`, and `.github/workflows/**`, are read-only here. Main AGENTS.md and sparks.json, WORKER_PROTOCOL.md, current open issue list, PR branch comparison and #48 dispatcher implementation were inspected. PR comparison against current main reports `diverged` and only this architecture file changed; integration/rebase must be handled by the owning B00 review process, not assumed conflict-free.

**Purpose and deliverable:** Publish a reviewable ticker-first research and reusable-worker architecture contract, with explicit compatibility, ownership, time/provenance, full-universe coverage, dispatch/manager integration, economic attribution, validation and retirement requirements. This branch does not implement providers, create canonical entities, deploy services or register queue tasks.

**Input authority:** Current main governance, current GitHub issue/PR state, source-linked B02/B03/B05 canonical contracts and #48 dispatcher; observed provider/market facts are not input to this architecture worker. **Output:** one proposed architecture specification consumed by B00 #24/#32/#48/#50, B01 #44, B02 #11, B03 #12, B08 #34 and B19 #17. Schema proposals are **not** effective until owner review and approved versioning. Unknown runtime entitlements and canonical registry membership remain unknown.

**Lifecycle mapping:** proposed `available` = no claim; `claimed` = `claimed`; `implementing` = `building`; `testing` = `building` with check evidence; `review-ready` = `review` or `component_verified` only after mandatory checks; `integration-blocked` = `integration_blocked`; `integrated` = `integrated` only after authorized merge and independent main validation; `retired` refers to conversation archival, **not** worker state `closed`. Preserve `withdrawn` and `closed` as defined by WORKER_PROTOCOL.md.

**Method:** discover current authoritative contracts → audit collisions → draft compatibility/invariants → falsify assumptions using actual repo paths and fixture cases → commit architecture-only changes → request receiver interface review → verify current head/PR changed paths → post machine-readable resolution where possible. Architecture document commits are review artifacts, not successful execution of ingestion/replay tests. A missing `entity.json` at a specific main path establishes only that the queried path was absent; it does not prove absence from every research registry.

**Failure register and mitigations:**
- F1: candidate ticker IDs conflated with admitted canonical entities → explicit admission reconciliation and coverage denominators.
- F2: dispatcher proposal mistaken for claimed/operational worker → separate task lifecycle and live adapter evidence.
- F3: multiple managers, queues or append journals → use #33/#25 and B02/B03 owner interfaces.
- F4: stale head-SHA/CI assertions → re-fetch PR head and workflow evidence before promotion.
- F5: multi-hop revenue double counting → distinguish final demand, intermediary recognized sales, financing and retained margin.
- F6: premature conversation closure mistaken for integrated PR → separate archive from GitHub integration.

**Acceptance matrix for #42:**
- A1 ownership and canonical path compatibility: specified in this document; receiver review outstanding.
- A2 reusable ticker-independent worker interface and provenance: specified; runtime tests not run.
- A3 safe staged migration, rollback and negative cases: specified; migration not performed.
- A4 dependency handoffs and disjoint branch scope: recorded in issues; recheck current PR overlap before merge.
- A5 integration, data-plane and complete-registry proof: explicitly **not verified** and owned by receivers.

**Single next unblocked action:** B00 reviews #43 against current main and B00 #50 graph contract, records accept/revise disposition and assigns an exact interface reconciliation to the existing #48/#33 owners. Do not alter #48 or #33 files from #42.
