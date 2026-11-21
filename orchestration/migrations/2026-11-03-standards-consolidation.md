# Standards-first architecture migration decision — 2026-11-03

**Task:** B00 #156, branch `work/156-standards-migration-decision`; **parent queue:** #136. **Read baseline:** main `25ae331f2774250528fc939e3e7795583f8808a3` verified 2026-11-03. This is a decision proposal and receiver handoff, not implementation or merge authorization.

## Decisions (user-authorized design choices)

1. **Simplify first.** Native GitHub Issues, PRs, worktrees, rulesets and Actions own development lifecycle. No new state database, registry, agent manager or MCP runtime.
2. **Universal capability contract.** Every *independently invoked or reused capability* (prompt, code, hybrid) must expose a stable typed input/output/error/version contract. Trivial internal functions inherit their enclosing capability's contract: do not generate one manifest per helper function. Reuse `component-blackbox.v1.json` proposed in B00 #103/PR #104; maintain one canonical component contract, not an alternative.
3. **Bounded Codex autonomy.** Discovery, estimation, scoped code edits, targeted retries, tests, commits, and draft PRs can proceed under task permissions. No merges/tags/releases, new secrets, cross-domain writes, or architecture contract replacement without authorized review. GitHub CI and permissions must enforce, not merely instruct.
4. **Existing-component pilot.** Retrofit one existing component from PR #104's matrix after inspecting its current merged/main and PR state. Prefer a small deterministic read-only component (e.g. B06 observed range calculation) with existing tests; do not mutate B06 PR #109/#145/#150 or create an overlapping branch. B00 chooses only after B06 ownership confirmation.

## Prior art and minimal workflow

- Contract-first / ports-and-adapters: consumers depend on versioned ports, not agent or implementation.
- Unix composability / single responsibility: minimum viable capability solves one useful problem, composes through contracts.
- GitHub flow and short-lived worktrees: task identity is persistent GitHub issue; branch is ephemeral change identity; conversation is replaceable.
- Test pyramid and consumer-driven contract testing: validate schema and semantics, regression and cross-component compatibility.
- Progressive-disclosure Agent Skills and compact AGENTS.md: task-specific instructions loaded as needed; deterministic controls live in checks/permissions.
- Functional core / imperative shell: pure calculations separated from provider or GitHub side effects.
- Measure accepted output per effort; prefer reuse > configuration > delta > new implementation. Never infer actual token usage from estimates.

**Future target workflow**: product outcome -> locate existing GitHub issue / code / capability -> classify REUSE / CONFIGURE / EXTEND / BUILD / BLOCKED -> identify only missing delta -> publish/confirm typed contract -> execute in isolated owned worktree -> domain + negative + consumer tests -> independent exact-head CI -> draft PR / approved merge -> verified main -> reusable reference. Preserve current branch-per-conversation requirement until B00 formally migrates it; do not silently bypass present AGENTS.md or sparks.json.

## Consolidation inventory and routing

| Existing artifact | Disposition | Exclusive owner / next delta |
| --- | --- | --- |
| B00 #103 / PR #104: `schemas/component-blackbox.v1.json`, `architecture/BLACK_BOX_COMPONENT_CONTRACT.md` | **AUTHORITATIVE CANDIDATE, EXTEND** | B00 #103 owns public manifest and envelope design. Decide universal boundary granularity, execution modes (`prompt`, `code`, `hybrid`), typed errors and contract test fixtures. No competing schema. |
| B00 #59 / PR #60: `orchestration/retirement_intake/**` | **REUSE** | B00 #59 owns source-pinned discovery; use discovery index as read-only projection, not a new authoritative registry. Verify refresh against live GitHub. |
| B00 #78 / PR #79: `orchestration/agent_adapters/**` | **EXTEND AFTER CONTRACT** | B00 #78 owns compact provider-neutral task envelope and GitHub resume, not per-conversation remembered state. Document/test prompt/code/hybrid adapters through same input/output contract. |
| B00 #106 / PR #107: `orchestration/worker_contracts/**`, `orchestration/tests/test_worker_v2_contract.py` | **REUSE / RECONCILE** | B00 #106 align to canonical worker status; avoid introducing another lifecycle or task ledger. B01 independently tests. |
| B00 #32 / PR #33: `orchestration/agentic/**` | **REUSE EXISTING LOGIC** | B00 #32 existing decision/retry logic; avoid competing execution controller. B01 #65 verifies exact-head negative tests. |
| B00 #138 and #24 / PR #25: queue and scopes | **DEPENDENCY / NO CROSS-WRITES** | B00 queue owner reconciles task-first policy and historical conversation-per-branch rule. Do not touch `orchestration/planner/**` or related scope files here. |
| B00 #132 / PR #133 and #134 / PR #135: Projects and Copier | **SEPARATE / GATE** | Projects is a derived display; native Issues remain authority. Copier can bootstrap future modules after scope failures fixed. #135 has strict worker-scope mismatch; no disabling validation. |
| PR #123: routing / `CLAUDE.md`, Copilot entrypoints | **RECONCILE BEFORE ADOPTION** | Nonstandard branch and overlapping instruction structures; B00 must evaluate rather than merge duplicate operating policy. |
| B01 #65 (handoff), #64 and #89 / PR #90 | **ENFORCEMENT** | B01 owns `.github/workflows/**`, `tests/integration/**`: add/verify exact-head tests of accepted #104 contract, nonzero test count, consumer regression, owned path checks; no B00 edits. |
| B08 #34 and PR #55 | **DEFER RUNTIME** | B08 owns `services/**`, `deployment/**`: MCP/REST/hosted controller only after pilot demonstrates cross-host requirement and entitlement/security/operational readiness. No new deployment now. |

**Collision rule:** Before any implementation worker begins, fetch *all* live PR changed-file lists and issue scope claims. Exact source paths and subtree overlap both matter; task status, green CI, and merging require live evidence. Draft PR means unintegrated.

## Pilot — one existing useful capability, not a new framework

**Candidate:** B06 `market.range_traversal` read-only observed range metrics, already represented by PR #104 and in existing B06 work (#109, #145, #150). B00 first confirms source module, its accepting owner and current use; select another accepted read-only module if this creates ownership collision.

- P1: Existing contract inventory discovers it by ID and pinned version; no duplicate implementation.
- P2: One small, documented delta added *only by its authorized B06 owner* after overlap check.
- P3: Same input/output schemas for code or prompt/hybrid alternative; no claims they are semantically interchangeable without fixtures/evals.
- P4: Tests include valid inputs, malformed/partial inputs, stale evidence, incompatible version, explicit nonpredictive output and regression of current consumers.
- P5: Independent B01 acceptance at exact PR head and subsequent main verification if authorized to merge.
- P6: A second consumer imports/invokes the contract without copying module logic.
- P7: Three actual work cycles, if telemetry available, record input/output/cached tokens, rework, retries and accepted criteria. Unknown costs remain `null`; do not invent ROI percentages.

## Ordered dependency and write allocation

**Gate 0 — B00 consolidation (#136, #156):** verify freshest main, all open PR changed paths, existing controller/capability schemas, instruction conflicts; publish this decision and identify superseded text. This draft has no authorization to edit AGENTS.md or shared schema.
**Gate 1 — B00 #103/PR #104:** finalize universal *public capability* contract; preserve compatibility, one format, scope-only changes inside existing exclusive owned files.
**Gate 2 — B01 #65 plus matching integration owner:** implement/test enforcement of Gate 1 and current orchestrator tests at exact head, including absence/skipped tests; work only in B01 paths.
**Gate 3 — B00 #59/#78/#138:** wire discovery + minimal task envelope + task-first resume by extending their own existing branches; no second registry or controller. In parallel reconcile Copier/Projects blockers only when required for pilot.
**Gate 4 — Existing B06 owner:** apply one minimal delta to existing component, contract fixture and second consumer without colliding with #109/#145/#150.
**Gate 5 — B01 independent verification:** exact-head tests and merge readiness; PR remains draft until approved. After approved merge, rerun main CI.
**Gate 6 — B08 #34, conditional only:** evaluate one hosted MCP adapter when cross-client reuse is demonstrated; no deployment preauthorization.

## One handoff to the existing B00 orchestrator (issue #136)

> **Orchestrator: integrate B00 #156 decision, do not launch another framework.** User preferences locked for this migration: SIMPLIFY / UNIVERSAL capability contract / BOUNDED CODEX / EXISTING COMPONENT pilot. Read latest main and all open issue/PR ownership and changes, then reconcile #103/PR104, #59/PR60, #78/PR79, #106/PR107, #32/PR33, #138, #132/PR133, #134/PR135, PR123, B01 #65 and B08 #34. Reuse the public black-box schema proposed on PR104 rather than creating an alternative; B00 decides whether any trivial helper can inherit a parent contract. Make GitHub issue the durable task identity, but first propose a coordinated migration of current AGENTS.md/sparks.json branch-per-conversation rule; do not silently violate it. Allocate exact non-overlapping paths to existing owners. Route contract validation to B01, defer B08 runtime, and pilot one existing B06 read-only component only after B06 confirms exclusive ownership and current code. Preauthorize Codex for bounded scoped discovery/implementation/tests/draft PR, never merging, cross-owner writes or disabling strict checks. Record three task-cycle costs only where measured; otherwise null. Deliver a single ordered queue of verified actions, unresolved gate IDs, and one next owner/action; do not commission new architecture documents or a new orchestrator. Source: B00 #156 and its draft PR. **Do not merge without user authorization.**

## Verification status

Read-only GitHub inspection confirmed main SHA and the above referenced open PR descriptions/changed paths (2026-11-03). No domain tests, CI, contract validation, cross-client runtime or user-facing pilot executed in this documentation-only change. Unknown means unknown, not pass. No current branch-protection/ruleset proof gathered. Next action: B00 #136 reconcile this decision with #103 contract work and assign the smallest existing-owner implementation delta.
