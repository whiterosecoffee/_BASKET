# _BASKET — Conversation Intelligence, Closeout and Project Maturation

**Protocol:** `basket.conversation_handoff@2` (draft; B00 review required)  
**Owner:** B00 · **Workstream:** Issue #169 / PR #170  
**Invocation:** **apply handoff prompt**

This is the authoritative *draft prompt* for this workstream. The companion Python CLI is a deterministic evaluator of supplied evidence, not a transcript reader or autonomous orchestrator. The full procedure below is intentionally richer than the CLI's current data model. Do not describe unimplemented extraction, semantic comparison, or GitHub verification as operational.

## Mission and success criterion

Review the entire **available** conversation as a source of (1) unfinished authorized work and (2) transferable project intelligence. Finish useful work within ownership, then preserve the highest-value principles, patterns, methodologies, architectural reasoning, decisions, counterexamples, failure lessons and concrete applications so the project matures rather than repeating discussions.

Success is **not** merely a status summary or a short handoff. An independent receiving session must be able to understand **what was decided, why, what was tried, what evidence supports it, which existing capability it affects, how to implement or test it, and what not to repeat**. The review must not create a parallel orchestration framework, duplicate backlog or unverified completion claims.

## Phase 1 — Reconstruct the actual work

1. Review the full available transcript, including user corrections, evolving requirements, assistant claims, tool results, failed attempts, design alternatives, approvals and reversals. State any transcript-coverage limitation.
2. Establish the original objective, latest controlling objective, authorized write scope, deliverables and acceptance criteria. Distinguish explicit authorization from recommendations.
3. Build a compact obligation ledger: **deliverable → owner → current state → evidence → missing criterion → smallest action**. States: verified, implemented/unverified, incomplete, blocked, transferred, out of scope. Do not collapse proposed, coded, tested, integrated, deployed and operational.
4. For repository work, read applicable current governance, relevant issue/PR, changed files and exact-head CI **only where current evidence changes disposition**. GitHub is authoritative for repository state; conversation summaries are not. Do not infer active workers from open PRs.
5. Complete authorized low-risk work now. Reuse existing issue/branch/owner; do not edit another worker's files, launch dormant workers, merge or release without authority.

## Phase 2 — Extract project intelligence at two levels

For every **material** insight, preserve a compact but complete knowledge unit:

- **Problem / trigger:** the recurring failure, need or opportunity.
- **Principle:** the transferable rule, distinct from the specific example.
- **Pattern and mechanism:** how the principle works; algorithm, workflow or interface.
- **Methodology:** ordered procedure, decision criteria, invariants, checks and recovery.
- **Concrete application:** ticker, component, research question, code path or episode.
- **Architecture:** boundaries, black-box input/output contracts, source of truth, dependencies, owners, data flow and consumers.
- **Prior-art/theory pointers:** concise family tags, actual mechanism, applicability and boundary; optional grounded reference.
- **Evidence and falsifiers:** source/revision, observed outcome, negative cases, counterexamples and uncertainty.
- **Decision record:** chosen approach, rejected alternatives, trade-offs, assumptions and conditions for reconsideration.
- **Maturation destination:** existing project capability, specification, test, runbook, issue or owner; adoption status.

Do not force all fields for routine facts. Do not reduce substantive architectural knowledge to three bare bullet points or a list of tags. Distinguish **principle, pattern, methodology, architecture and example**; they are not synonyms. Preserve the causal reasoning that makes a lesson reusable.

### Prior-art and internal taxonomy

Use established families where helpful: design by contract (DBC), ports/adapters (HEX), modularity (MOD), dependency graphs (DAG), event sourcing (EVS), CQRS, idempotency (IDEM), point-in-time logic (PIT), provenance (PROV), falsification (FALS), reproducibility (REPRO), state machines (FSM), postmortems (POST), information compression (INFO), decision theory (DEC), observability (OBS), and other applicable families.

**No arbitrary maximum on tags or taxonomy families.** Each tag must communicate a real mechanism. Unknown or missing families signal **taxonomy-review work**: first check existing vocabulary, then propose a distinct family if needed. Do not automatically canonize new labels or create a new issue for every gap. Tags are pointers to reasoning, not evidence of correctness. If a family is asserted as historical prior art, distinguish an analogy from a verified citation.

## Phase 3 — Retrospective execution audit

Score the ten observable dimensions 0–5, N/A where unsupported: objective control; execution conversion; reuse; ownership; verification; dependency handling; resource efficiency; knowledge extraction; handoff quality; closure discipline. Normalize across applicable dimensions. This is a judgment aid, **not a completion percentage or measured productivity metric**.

For up to three material execution failures, provide:
**actual path → contemporaneously feasible better path → root cause → reusable preventive mechanism → existing owner/capability → acceptance test**.

Evaluate decisions with the information and tools available **at that time**, not hindsight. Do not penalize external blockers, invent token/time savings, or create improvement work merely to raise the score. A low score does not automatically block archiving.

## Phase 4 — Reconcile, synthesize and rank maturation

1. Compare every material knowledge unit against authoritative existing contracts, code, issues, tests, runbooks and decisions. Classify **reuse / extend / replace / duplicate / conflict / supersede / new gap**.
2. Identify contradictions among conversation statements, code and newer evidence. Preserve both claims and their dates; resolve only with evidence. Missing source is unknown, not false.
3. Evaluate relevant prior-art families and alternative patterns. Choose the **lowest-complexity approach** meeting the requirement; explicitly note why alternatives are unnecessary or inferior. Do not reinvent schedulers, queues, registries or stores.
4. When useful, rank candidate improvements on 0–5 **reusability, impact, novelty, evidence, feasibility, risk reduction** (max 30). Override scoring for critical correctness/data-integrity failures. State implementation effort and coordination cost as estimates, not facts.
5. Give each insight a disposition: **already incorporated / consolidated / transfer / proposed / deferred / discarded**. Prefer updating an existing authoritative artifact. Keep research hypotheses separate from approved policy.
6. Preserve key ideas even when not yet actionable: the destination may be a concise decision record or an existing owner handoff rather than a new task. Avoid silent loss of valuable architecture simply because implementation is blocked.

## Phase 5 — Execute and consolidate

Finish authorized code, tests, corrections or documentation within exclusive paths. Use the smallest existing integration surface. For each change, record exact SHA, paths, test commands, actual results and CI run if available. Do not call a shared green workflow domain acceptance unless its job actually executed required tests.

Separate **knowledge recorded**, **decision accepted**, **implementation executed**, **independently verified**, **merged on main**, and **operationally observed**. Existing worker task/resolution contracts remain authoritative; this protocol is a review aid, not a competing lifecycle.

If another owner is needed, reuse the existing receiving issue. Persist only material new information where authorized. Posting a handoff does not prove receipt or execution.

## Phase 6 — Mandatory complete handoff when required

When the final disposition is **Hand off before archiving**, ALWAYS produce one **self-contained, ready-to-paste orchestrator prompt**, even when a GitHub handoff already exists. Its required structure is:

1. **Receiver and authority:** functional owner, repository, existing issue/branch/PR, last checked head SHA, scope and forbidden writes.
2. **Mission and acceptance:** the precise remaining deliverable and independently verifiable completion gate.
3. **Do not repeat:** verified completed work, existing tools and artifacts to reuse, failed attempts and why they failed.
4. **Knowledge transfer:** material principles, patterns, methodologies, theory-family tags, architecture and black-box interfaces, specific applications, rationale, rejected alternatives, limitations and falsifiers. Preserve causal links; do not truncate to bare tag names.
5. **Dependency and execution sequence:** current authoritative state refresh, smallest first executable action, follow-on work in dependency order, independent tests and CI, escalation conditions.
6. **Evidence and resolution:** exact commands and source references where known, unknowns, adoption/defer decisions, one next owner action and retirement conditions.

Reuse existing destination; no duplicate workstream. Clearly mark handoff **generated / posted / accepted / executed**. If transfer is not necessary, do not manufacture one.

## Phase 7 — Archive decision and output

Check that no authorized executable local task, required decision, promised follow-up or valuable untransferred knowledge remains. Unrelated project backlog does not block a local closeout. Select exactly one:

- **Continue here:** required authorized work can still be done locally; execute it first.
- **Decision needed:** required authority cannot be obtained or appropriately transferred.
- **Hand off before archiving:** local scope exhausted, remaining work has an owner, and a complete copyable handoff is included.
- **Ready to Archive:** all applicable local work and knowledge dispositions are complete; no transfer remains.

Final response should be **concise in its overview, complete in its handoff**:
(1) disposition, (2) verified work and evidence limits, (3) execution-quality score and top three observed corrections when material, (4) **knowledge map** of material principles/patterns/methodologies/architecture and their destinations, (5) remaining owner/blocker, (6) full handoff prompt if required, (7) exactly one next action.

End with exactly one standalone line and nothing after it: `Continue here`, `Decision needed`, `Hand off before archiving`, or `Ready to Archive`.

## Retrieval and compatibility

**Invocation in any conversation:** `apply handoff prompt`. The receiving assistant must retrieve this file from `whiterosecoffee/_BASKET` at `orchestration/conversation_closeout/HANDOFF_PROMPT.md`. Read from main only after integration; until then read branch `work/169-conversation-closeout-cli`. Do not pretend retrieval occurred if unavailable. The invocation is natural language until registered in project instructions.

**Offline optional evaluator:** `python -m orchestration.conversation_closeout --input evidence.json --output closeout.md`. It processes reviewer-supplied evidence; it cannot read ChatGPT transcripts, verify GitHub claims, perform semantic deduplication or implement this entire methodology automatically. The richer prompt is the controlling analysis procedure; do not downscope it to the CLI's currently limited fields.

## Revision and quality gates

Keep this as a versioned, evolving protocol. Each material revision should identify: observed failure or lost insight; prior version behavior; precise correction; test/pilot fixture; measured or observed result; owner and exact revision; compatibility impact. Test at least routine, research-heavy and repository-implementation conversations before promoting to authoritative policy. Compare **knowledge retention and handoff actionability**, not merely score reproducibility.

**Current state:** Draft specification, not integrated main policy. B00 owns review. Do not merge or release without authorization.
