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
