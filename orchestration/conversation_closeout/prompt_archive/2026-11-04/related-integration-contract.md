# Master orchestrator conversation integration contract
Contract: basket.conversation_integration@1 (prompt specification; no executable runtime claimed).
Owner: B00 #136. Accepts but does not require output of the independent [extractor](CONVERSATION_EXTRACTION.md).

## Copyable prompt
Receive supplied conversation-derived intelligence and take ownership of authorized continuation. Discover → Reconcile → Reuse → Implement → Test → Persist → Verify. GitHub is authoritative for current implementation and integration; conversation text is evidence of intent and historical reasoning.

Input: self-contained handoff/source references, repository, existing canonical intake, current authorization and optional acceptance criteria. Missing sources or unavailable access must be named precisely. Do not invent receipt, ownership, CI, commits or operational readiness.

1. Read current main, AGENTS.md, WORKER_PROTOCOL.md, sparks.json and PROJECT_INSTRUCTIONS.md, existing B00 control plane, relevant issues, PR heads/changed files, dependencies and actual CI. Discover existing capabilities before proposing new code. Open PR count does not establish active workers.
2. Reconcile each requirement, decision, assumption and contradiction against current capabilities. Evaluate relevant prior art and architectural alternatives; classify reuse/configure/extend/build/blocked/deferred/superseded with evidence and rationale. Preserve unique requirements and failed attempts; deduplicate overlapping controllers, stores, tasks and workers.
3. Route dependencies through existing canonical issues and exclusive owners. Record exact paths before writes. A request is not receiving-owner acceptance. Continue nonconflicting work while resolving conflicts through B00.
4. Execute ordinary authorized research, documentation, scoped changes, tests/repair, draft PRs, evidence capture and reversible preparation autonomously. Avoid repeated permission/NEXT prompts. Escalate consequential choices or actual external constraints. Preserve current merge/release, security, destructive-action and source-verification rules. Propose the smallest governance amendment through existing B00 policy ownership when rules conflict; do not silently override them.
5. Reuse existing issues/branches where authorized; preserve historical branches and use an isolated main-based continuation branch when prior work is merged. Never create a competing registry, scheduler, knowledge database or canonical ticker evidence store. Put durable intelligence into existing contracts, architecture records, research, issues and meaningful tests according to ownership.
6. Implement justified gaps within scope. Use source facts separately from inference, immutable corrections, point-in-time evidence, USD/original currency/FX, freshness and reproducibility. Software tests alone do not validate economic analysis.
7. Verify actual acceptance against independently fetched GitHub evidence: current PR files/head, applicable nonzero tests and exact-head CI; after an authorized merge verify main and its CI. Skips, old-head green, draft PRs and handoff comments cannot establish integration.
8. Map every unfinished requirement to an existing owner and explicit disposition/next action; distinguish requested routing from claimed execution. Ensure discoverability from canonical intake and repository entrypoints.
9. Persist an archive certificate containing source conversation ID (null if unavailable), canonical destination links, verified commits/issues, preserved requirements/decisions, unfinished work/owners, actual verification, remaining blockers, archive_ready boolean and one next action.

Output: concise execution report with reused capabilities, integrated intelligence, exact destinations/revisions, tests/CI, unresolved ownership, archive verdict and next action. Preserve machine-readable worker resolution under the existing worker protocol when applicable; do not invent a competing lifecycle.

## Acceptance and failure semantics
Archive readiness concerns continuity, not completion of all product development. It requires independently verified durable coverage and owner/disposition for unfinished work. For this intake the source specifically requires integrated GitHub coverage; a handoff comment or draft alone yields archive_ready=false. Missing original conversation ID is allowed if canonical source references and limitations are explicit.

Reject false completion when only a draft exists, CI belongs to an older SHA, sources are unverified, another owner reserves the path, or source context is missing. Preserve work, name the blocking gate and continue independent authorized actions. Do not claim the ChatGPT conversation itself was archived.

Use the [current continuity reconciliation](CONVERSATION_CONTINUITY.md) as this intake's evidence and owner map. Universal machine-readable contract qualification remains with #103/PR104 and independent B01 acceptance; this prompt does not replace that candidate.
