# B00 worker v2 — contract compliance and acceptance audit

Identity: B00; issue #106; branch `work/106-worker-v2-contract-audit`; parent/coordinator B00. This conversation is a B00-owned contract-audit worker, not the owner of other sparks' implementations. Exclusive writes: `orchestration/worker_contracts/worker-v2.md`, `orchestration/tests/test_worker_v2_contract.py`. Read-only: AGENTS.md, orchestration/sparks.json, orchestration/WORKER_PROTOCOL.md, schemas/worker-{task,resolution}.v1.json, orchestration/worker_protocol.py, issue/PR/CI evidence. No edits to CI, provider adapters, ticker research, shared schemas, B00's other active PR paths, or main.

Purpose: confirm worker claims fail closed against fresh repository evidence, formalize repeatable work and explicit dependencies, and surface gaps to B00. Downstream consumers: B00 evidence evaluator and B01 independent CI. Success: tests, exact-head evidence and PR review; failure: invalid ownership, stale CI, unsupported provenance or missing gates. A draft PR is not integrated.

Canonical lifecycle mapping (no new enum values): Available = unclaimed planner proposal (not a worker-task state); Claimed = `claimed`; Implementing = `building`; Testing = `building` until evidence validated; Review-ready = `review` and separately an independently evidenced `component_verified` disposition; Integration-blocked = `integration_blocked` resolution (task remains `review` or `blocked`); Integrated = `integrated` only with merged PR and independent main-CI check; Retired = `closed` or `withdrawn` after recorded reason. The evaluator also has derived evidence phases; these are NOT task status values.

Interfaces: one issue-held `basket.worker_task@1` JSON claim, one final comment `basket.worker_resolution@1`, live `basket.github_evidence@1` from B00, and versioned paths in the catalog. Required inputs: exact issue number/url, branch and base, spark, permitted paths, named acceptance, dependency issues, PR file list, head SHA, workflow-run URL/SHA/conclusion. Outputs: dated issue/PR report, immutable run evidence and evaluator result. GitHub source is authoritative for ownership and integration; provider entitlements are explicit; never infer market freshness from GitHub. All data assertions require classification, effective/observed/available/ingested times where applicable, source URL, revisions, FX basis and explicit stale/unknown status.

Process: Discover existing issues/PRs → acquire authoritative instructions and evidence → normalize contract metadata → verify exact branch and path scope → reconcile dependencies and source revisions → calculate deterministic acceptance → persist to issue/branch → validate offline + independent QC → publish draft PR → invalidate consumer assessments when PR head, source revision or relevant dependency fingerprint changes. Idempotency key for this audit: issue + exact head SHA + evidence snapshot hash + evaluator version. Never reuse an old pass when any constituent changes.

Operational policy: before each material mutation refresh ownership and PR changed paths. On collision, preserve state, create minimum receiving handoff, continue disjoint work. On transient provider failure retry with bounded backoff and checkpoint, retaining attempt failures; on authorization/entitlement failure stop that dependency and report missing proof. On partial execution, resume from immutable input manifests and verified checkpoints; repeated run must not mutate successful observations. No centralized mutable state or parallel scheduler is introduced.

Validation/failure register: unowned paths, mismatched PR file list, stale or absent head-aligned CI, missing mandatory acceptance, a purported pass with no evidence, unauthorized merge, stale market observation and duplicate consumption must not be counted as verified. Domain unit tests establish only local capability; B01 exact-head CI, approved merge, and main CI are distinct gates. Independent security/schema reviews and operational provider deployment are not claimed by this contract.

Acceptance matrix: A1 lifecycle and interface mapped (document); A2 negative evidence tests (local suite); A3 B01 exact-head CI and B00 integration review (outstanding until verified). Improvement queue: 1) close evidence gaps from test results; 2) independent exact-head validation; 3) approved integration and main-CI check. Schema changes, a generalized new black-box interface, and scheduler changes are deliberately excluded (see #103).


## GitHub-managed standardized worker model — 2026-10-29 scope clarification

The worker is **not** the chat. Distinguish the reusable **definition** (capability profile + versioned contracts + permissions), **instance** (agent/runtime identity with entitlements), **assignment** (issue-bound authorization, unique branch, dependencies, path lease), and **attempt** (immutable execution/checkpoint/result/evidence). Existing reusable profiles and recipes: `orchestration/planner/worker-library.json`. Existing task/resolution contracts: `basket.worker_task@1`, `basket.worker_resolution@1`. Do not create a second planner, controller or state schema.

GitHub is the authoritative control-plane ledger for definitions, assignments, branch/PR artifacts, reviews and Actions CI. It is not a persistent execution host or live tick store. The **existing** agentic controller under `orchestration/agentic/**` (#32) should own claim scheduling, heartbeat/lease recovery, attempts and dispatch policy; agent-neutral adapters (#78) translate assignments to ChatGPT/Codex/VS Code/other agents; B08 owns supervised runtime/deployment; B01 owns independent CI. Issue #103 owns black-box component I/O schemas. This worker #106 only records contract alignment and fail-closed negative tests.

Suggested dispatch lifecycle:
1. **Discover:** read live GitHub issues, exact PR changed paths, registry capabilities and source-revision fingerprints; do not infer activity from PR state.
2. **Match:** choose definition by required capabilities, allowed spark paths, input/output contract versions, credentials/entitlements and available runner, without creating dormant branches.
3. **Authorize:** B00 records issue-bound task claim; reserve noncolliding paths; create a unique main-based branch for the conversation/run; task proposals are not executable claims.
4. **Dispatch:** an authenticated runtime hands an immutable task envelope to an eligible instance; worker uses only authorized paths, bounded retries and idempotent checkpoints.
5. **Observe:** heartbeat/lease, attempt IDs, source fingerprints, exact commit and structured errors. Expired lease is unknown/lost, not proof of completion.
6. **Validate:** domain-owned tests plus independent B01 exact-PR-head CI; reject zero-test, skipped-required checks, mismatched SHA, source staleness or paths outside claim.
7. **Review/publish:** draft PR then B00 reconciliation; explicit user authorization before merge/release, main-CI verification afterward. Emit dependency fingerprint changes for downstream recomputation.

Failure policies: duplicate assignment → reject or reconcile by stable task key; PR collision → quarantine affected paths and issue owner handoff; runner lost → recover checkpoint with a new attempt and fencing token, never assume previous attempt stopped; no credentials/entitlement → block dependent fetch only; changed input → invalidate calculated results, retain immutable history; stale CI → rerun at current head. GitHub Actions can verify finite jobs but cannot supply an always-on authenticated data worker.

Implementation owner routing (nonblocking design handoffs, not claims of completion):
- **B00 #32**: existing agentic controller dispatch/lease/retry/attempt integration; do not duplicate here.
- **B00 #78**: adapter-specific task transport and VS Code launch packets.
- **B00 #103**: black-box component contract schema, distinct from worker assignment.
- **B01**: independent exact-head and adversarial CI acceptance.
- **B08**: persistent supervised agent/runtime and durable market data-plane hosting.
- **B02**: market data ingest/revision/freshness execution.

Near-term acceptance target: one real issue → deterministic worker match → unique branch → reproducible offline execution → commit/draft PR → exact-head CI → B00 verification. Repeat with two distinct worker profiles and a deliberate path collision before claiming cross-agent autonomous orchestration. No unverified autonomous execution or hosted service is claimed.


## GitHub Copilot implementation handoff

**Scope:** Existing issue #106 and PR #107 supply verified governance contracts and negative tests. Do not treat this as authority to edit controller or adapter paths under this branch. Open a new issue and uniquely scoped branch for any new implementation worker, only after inspecting current main, sparks registry, open PR changed paths and owning issues. Coordinate with B00 controller #32, adapter #78, component contracts #103, B01 CI and B08 deployment.

**Copilot objective:** Prove one actual GitHub issue -> authorized worker profile match -> provider-neutral launch packet -> execution attempt -> branch commit -> draft PR -> exact-head CI -> B00 acceptance, using existing orchestration components. Avoid inventing another scheduler, task queue, contract schema or mutable source-of-truth. First identify what is already executable. Declare all unavailable runners/credentials and do not simulate a completed external-agent dispatch as real execution.

**Required evidence:** exact main and task/PR head SHAs, authorized write paths, provider/entitlement status, commands and outputs, attempted/actual dispatch transport, immutable attempt and fencing identifiers, CI run URLs at exact head, recovery and collision negative tests, failure/retry journal and one next action. Red/absent CI remains a blocker. User authorization is required before any merge.

**Acceptance gates:**
1. Existing components discovered with links and actual implementation maturity; no overlapping writes.
2. One end-to-end issue-backed run with recorded genuine executor identity and task envelope (or explicit external-runtime blocker if it cannot execute).
3. Second role/profile with deterministic capability matching, and a rejected conflicting path claim.
4. Simulated lost heartbeat/restart with stale fencing token rejected, without claiming actual host recovery.
5. Head-aligned independent B01 CI, immutable results and B00 review; no self-merge.

**Read-first references:** AGENTS.md, orchestration/WORKER_PROTOCOL.md, orchestration/sparks.json, orchestration/planner/worker-library.json, orchestration/agentic/**, orchestration/agent_adapters/**, #32, #78, #103, #106, PR #107. GitHub stores control-plane evidence but is not an always-running execution host.


## Broad maturation plan and acceptance — 2026-11-04

**Assessment scope:** This is an evidence-qualified score for the standardized-worker solution, NOT overall _BASKET economic analysis or release readiness. Source anchors: issue #106/PR #107 at `eb099d8e2bf37918eaf11a46341289ff09651d9e` (63 orchestration + 29 integration/adversarial tests, Actions 40927765356); main `orchestration/worker_bridge/README.md` (issue #136, operator-mediated host-agent execution and independently reviewed failures); controller #32 and adapter #78 remain version-pinned dependencies, B08 #34 is the hosted-runtime owner. A green Actions run does not prove autonomous transport. Recheck live refs before every integration decision.

### Scored maturity rubric (judgment, 0–5 per axis)

| Dimension | Score | Evidence / missing gate |
|---|---:|---|
| Governance and path ownership | 4 | Spark paths, issue-bound claims and collision checks; branch-to-main integration remains gated |
| Reusable worker contracts | 4 | Profiles/library, worker task and resolution, agent assignment, source-pinned bridge; some dependencies unmerged |
| Worker selection and execution | 3 | Bridge selects profiles; operator-mediated actual host execution; unattended dispatch absent |
| Independent validation | 4 | B01 CI and negative tests with exact heads; live multi-provider integration not validated |
| Dependency and integration management | 3 | Explicit owner handoffs and pinned revisions; unresolved main/PR drift and dependency merges |
| Provenance and freshness | 3 | Contracts require source/revision/availability; incomplete live entitlements and full domain coverage |
| Durable restart and idempotency | 3 | Append-only attempts and fixture fencing tests; production crash recovery unobserved |
| Security and entitlement enforcement | 2 | Explicit claim, lease, sandbox and secret boundaries; hosted credential/tenant isolation unproven |
| Unattended hosted operation | 1 | B08 service is read-only snapshot; no verified persistent autonomous agent supervisor |
| Observability and cost control | 3 | Attempts and QA receipts are preserved; operational health/cost baseline incomplete |

**Total 30/50.** Score measures evidence maturity, not completion or speed; untested provider claims never receive operational credit. Do not convert scores into financial forecasts or release claims.

### Planned sequence, priority and exit tests

**P0 — Contract and ownership consolidation (B00 #106, #136; no new framework).** Preserve one source of truth for definition/profile, instance, issue assignment, immutable attempt and exact-head resolution. Check active PR changed paths, all task claims, canonical state vocabulary, pinned controller/adapter versions and B01 discovery coverage. Acceptance: every feature maps to a single owner/contract; zero unreviewed path collisions; #106 status/report reflects latest head and CI; historically stale packets fail closed. The #106 file and its existing negative tests are the only direct write scope of this conversation.

**P1 — Authenticated finite host-runner proof (B08 existing #34/#53, B00 bridge #136 read-only).** Build the *smallest* B08-owned supervisor transport for one authorized bridge packet with bounded execution, secret injection, durable attempt/fencing receipts, health, restart and cancellation. Do not conflate this with market-price ingestion or a new scheduler. Acceptance: real authenticated remote call, exact source/task fingerprints, no secret leakage, restart without duplicate publication, stale lease rejected. A local mock cannot pass the remote gate.

**P2 — Independent adversarial gate (B01).** Test rejected unknown/expired lease, cross-owner path, duplicate request, lost runner, replayed attempt, stale source/PR head, missing entitlements, unauthorized request, forged receipt, truncated/zero-test CI. Execute tests against actual receiving PR head; require no skipped mandatory tests and a separately recorded review. A current green #106 run is not evidence of B08 hosted security.

**P3 — Portability and second-worker proof (B00 #136; #78 contract).** Match two existing library profiles with different write permissions and task envelopes. Execute a second genuine bounded task after P1/P2. Compare complete inputs, outputs, receipts and cost/effort instrumentation; reject ungrounded productivity claims. Acceptance: no duplicate branch, no privilege escalation, deterministic task selection, both jobs independently auditable.

**P4 — Provenance through consumers (B02/B03/B05/B06).** Bind source revision, available_at, ingested_at, effective period, USD FX basis, TTD, schema/model version and dependency fingerprints through the economic graph/market traversal. Change a primary revision and prove only affected downstream computations invalidate; preserve historical results and corrections. Acceptance: point-in-time replay and missing/expired data rejection, not synthetic current marks.

**P5 — Operability and scaling (B08 + B00).** Instrument verified latency, retries, health checks, token/provider costs where obtainable, crash recovery, duplicate suppression and fail-closed overload controls. Increase concurrency only after observed SLO compliance with owner approval; never infer worker availability from PR count. Acceptance: measured dashboard and runbook, with a tested rollback and permission boundary.

**P6 — Integration/release (B00/B01).** Refresh main and review PR dependencies, migration/version compatibility, schema policies, exact-head CI, authorized merge and green post-merge main CI. Release and runtime deployment remain distinct separately authorized claims.

### Mechanisms, counterexamples and prior art

- **Design by contract / state machines:** task `claimed` is not executor activity; `component_verified` is not `integrated`; only exact evidence permits promotion. A passing CLI packet renderer without executing an agent is a negative example.
- **Ports/adapters / modularity:** the existing #136 bridge composes #32 controller policy and #78 assignment contract; a new dispatch queue would introduce competing authority, therefore rejected.
- **Event sourcing / idempotency / fencing:** append attempts and corrections; grant a fresh attempt on recovery; reject any late receipt from the old fence. An expired heartbeat is unknown activity, not permission to steal its write scope.
- **Dependency DAG / provenance / point-in-time replay:** stable input/source revision fingerprints selectively invalidate downstream computations; a current CI pass tied to an earlier SHA is stale for a changed PR.
- **Zero-trust boundary / observability:** an authenticated shell process is not a per-file OS ACL, and a local test does not attest the remote runner; enforce host permissions, redact secrets and compare publication diff to task scope.
- **Postmortems / falsification:** retain failed native Codex CLI initialization and QA-discovered authorization defects, with exact tested revisions and corrective reruns; do not conceal failures in aggregate green status.

### Effort/risk ranking and lifecycle decision

P0 is low estimated effort and high risk reduction; P1–P2 have the highest functional value and external integration cost; P3–P5 are conditional on P1–P2. Do not schedule additional workers or change shared schemas merely to represent this plan. Completion of this document is **contract knowledge recorded**, not proof that P1–P6 were executed. Store status in existing GitHub issues and the canonical `basket.worker_resolution@1`, not a second backlog file.
