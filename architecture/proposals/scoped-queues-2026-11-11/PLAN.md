# Scoped queues and shared-worker integration plan

Date: 2026-11-11. Status: design proposal, not a deployed scheduler or an allocation of active workers.

Planning branch: `work/scoped-queue-integration-plan-20261111-170133`.
Base: `74d913e8913d630d85451344689e093aeea07efc`.
Exclusive change: this document. Existing planner, schema, adapter, workflow and feature branches are not modified.

## Decision

Use one canonical GitHub issue inventory with scoped workstream queues. A branch implements an assigned slice of a workstream; it does not own a separate authoritative task database. Give each active feature worker a small ordered view of its permitted work. Route shared functionality to a provider worker on its own scoped branch, then consume a verified, pinned result.

The stable queue identity is the canonical issue/workstream, not a branch name. Branches can merge, be replaced or be transferred without losing pending work. Use the branch as an execution reference. Keep the project-level outcome order in #136 and project views; local ordering must respect that order and dependency gates.

This extends the existing [branch/lane plan](../../BRANCH_PLAN.md), whose queues are filtered views of one inventory. It does not introduce another controller, scheduler, framework or always-running agent.

| Option | Benefit | Cost / failure mode | Decision |
|---|---|---|---|
| One flat global execution queue | Simple central visibility | Coordination becomes a bottleneck; every task competes for a global order | Retain only for outcome priority |
| Independent queue per Git branch | Worker autonomy | Duplicate tasks, stale status, lost work after branch deletion, conflicting dependency claims | Reject as an authoritative ledger |
| Canonical issues plus scoped queue views | Local execution with shared identity, evidence and dependency visibility | Requires explicit scope and conflict rules | Adopt incrementally |
| Separate Project or runtime per branch | Strong visual separation | Fragmented inventory, extra APIs, lifecycle and permissions overhead | Defer unless an access boundary requires it |

## Current integration baseline

Evidence is dated; issue and branch states must be refreshed before execution.

- [#136](https://github.com/whiterosecoffee/_BASKET/issues/136) is the canonical coordination queue. Its current plan keeps a rolling horizon of at least 25 concrete actions, prioritizes the smallest useful outcome and defers unnecessary medium/large expansion. A local worker does not need to manufacture 25 subtasks; start with 2–5 actionable steps within its current outcome.
- [Component quickstart](../../COMPONENT_QUICKSTART.md), the existing component schema and `orchestration.component_conformance.check_exchange` are on the base main revision. Reuse typed boundaries, immutable references and consumer verification rather than copying validators or algorithms.
- [#134 / PR135](https://github.com/whiterosecoffee/_BASKET/pull/135) owns Projects synchronization. It is still draft at the inspection revision `2fbfd085d83cdcdfd264fdd3545339739bf890c8`. Explicit project selection and order-only behavior are available on that branch; full-sync and operational acceptance remain separate gates.
- That newer PR135 revision also adds opt-in `include_component=true` to its existing Copier template: a runnable empty-domain specimen with queue-first `HANDOFF.md`. Use it only where a new component genuinely needs scaffolding, pin the template revision and fill the actual issue/owner/branch/scope before domain work. The specimen's unassigned placeholders and successful empty payload are not a worker claim or qualified shared capability.
- [#24 / PR25](https://github.com/whiterosecoffee/_BASKET/pull/25) owns existing planner/scope work. `queue.json` is planning input, not an independently authoritative live completion ledger.
- [#78 / PR79](https://github.com/whiterosecoffee/_BASKET/pull/79) and the existing worker bridge supply assignment/handoff seams. Contract or packet generation does not establish a connected external executor.
- [#217 / PR218](https://github.com/whiterosecoffee/_BASKET/pull/218) and [#219 / PR220](https://github.com/whiterosecoffee/_BASKET/pull/220) supply a real producer/consumer pilot. Their publication and verification gates in #136 must be resolved by their owners; this plan grants no bypass.
- Private board exports, item IDs, operational snapshots and licensed inputs are excluded from this public document. They remain in authorized private evidence storage.

## Authority and queue contents

| Layer | Owns | Must not infer |
|---|---|---|
| Project coordinator | Outcome priority, cross-workstream dependencies, resource allocation and scope transfers | An open PR means an active worker |
| Workstream queue | Ordered references to canonical issues, local steps, next eligible action and dependency explanations | Local rank overrides a project dependency or grants new scope |
| Assigned worker | One bounded attempt, one scoped branch/worktree, tests and result publication | Provider files or shared CI are writable because the consumer needs them |
| Shared provider worker | Reusable capability changes and its own acceptance evidence | Passing provider tests proves every consumer works |
| Independent verifier | Exact-source checks and affected consumer evidence | Shared green CI proves unexecuted domain suites |

Start with a checklist or linked sub-issues in the existing canonical workstream issue. Keep short implementation steps in that checklist; create a separate canonical issue only when work has its own owner, deliverable or independently tracked acceptance. A shared request may serve several consumers without creating one duplicate task per consumer.

The minimum queue entry names: canonical issue, useful outcome, workstream, ordered step, actual assignee or unclaimed state, active branch/PR when present, exact authorized paths, dependency references, acceptance evidence and one next action. Derive branch head, CI and integration state from GitHub when needed. Store only measured effort; unknown cost/capacity stays unknown.

Reuse existing worker-task, resolution and evidence contracts. Any missing representation must be proposed through the existing contract owner; this document does not silently add fields or status values to production schemas. The existing handoff-request proposal is a starting point, not proof of a registered executable API.

## Shared functionality delivered by external workers

External means outside the consumer's write scope. The provider can be another authorized Codex task, another connected agent, or a human worker; no new vendor subscription or remote execution is implied.

1. Consumer identifies an existing capability and provider before requesting new code. Prefer reuse, configuration or a thin adapter.
2. Link the request to one canonical provider issue. Specify input/output meaning, required behavior, error cases, compatibility, exact paths, acceptance and affected consumers.
3. Coordinator resolves scope conflicts and issues a bounded assignment. Provider acknowledges or records a concrete rejection/defer reason. A request alone is not an accepted claim.
4. Provider works on its own scoped branch/worktree. Keep one writer for the actual path/resource set, including tests, schemas and generated files. Disjoint workers may run concurrently; conflicting work is narrowed or sequenced. Transfers are recorded, not treated as permanent ownership bureaucracy.
5. Provider returns exact source SHA, contract/schema versions, artifact hashes, executed test evidence and limitations through the existing resolution mechanism.
6. Consumer pins that immutable dependency and runs its own compatibility, negative-case and replay tests. Do not import a moving branch tip, vendor the provider implementation, or cherry-pick shared files into each consumer branch as a routine dependency mechanism.
7. Branch-level composition may proceed against a qualified source pin before main integration when its acceptance permits it. Label it branch-tested/accepted. Claim integrated behavior only after the dependency and consumer are on verified main; operational behavior requires actual runtime evidence.
8. A relevant provider change invalidates affected consumer evidence. Consumers may retain an older compatible pin with its limits recorded; they do not silently upgrade. Integrate providers before dependent consumers when required by the main build.

Use the current #217 producer → #219 consumer → existing B01 gate as the pilot. Use #134 for projection behavior and #78 for worker packets. Do not make the comparison feature implement a new queue engine or provider runtime.

## Eligibility, concurrency and failure handling

A selected task needs verified input/dependency evidence, compatible versions, an authorized scope, an actual available executor and the necessary resource permissions. Priority alone never means ready. A blocked shared request blocks only dependent actions; the workstream can continue independent eligible work. Detect cycles and return the smallest unresolved contract decision to the coordinator.

Reuse existing claim/attempt/lease mechanisms. A claim needs an issue/attempt identity, worker, branch, scope and expiry/fencing information where the existing implementation supports it. A local JSON lease is not a distributed lock. Until an enforceable atomic claim exists, serialize assignment through one coordinator instead of promising safe multi-host autonomous claims. Recovery must inspect the existing attempt and remote state before retrying.

Define concurrency scope by effect:

- **Code publication:** expected branch head, exact changed paths and relevant input/contract identities. An unexpected head or scope overlap stops publication.
- **Board field update:** target item identity and expected prior value. Preserve unrelated fields, statuses and priorities; reread after an uncertain response before retrying.
- **Global item ordering:** ordering is a shared resource. Serialize writers; verify membership and relevant order immediately before and after writes. Preserve unselected relative order. GitHub provides no atomic transaction covering a multi-item reorder.
- **Scoped queue views:** a local rank can remain in its canonical checklist initially. Do not translate every branch's local reorder into global native board moves. Add a separate scoped-rank representation only if two real consumers demonstrate that the checklist/view is insufficient.

For order-only inspection, propose narrowing repository evidence collection to the selected canonical issues and necessary owner/dependency facts, while retaining complete board identity/order checks for a global reorder. Do not waive board-membership drift or missing-member checks. Unrelated repository commits need not invalidate an order operation unless they affect its declared evidence. This is a proposed #134 improvement, not a permission to bypass current guards.

Separate retryable transport failures, rejected writes, ambiguous mutation outcomes and evidence drift. Preserve failed attempts. Repeated global rescans during unrelated activity are a reason to improve the existing collector, not to build another controller or hide failures.

## Minimal integration sequence

These are proposed owner-routed steps, not claims that assignments were accepted. Keep #136's current runnable-comparison priority; queue integration proceeds alongside independent work.

| Step | Existing owner / dependency | Deliverable and exit condition |
|---|---|---|
| 1 | Coordinator #136 | Choose one producer/consumer pilot and record its outcome, scope and current gates |
| 2 | Existing feature owners #217/#219 | Add small local checklists referencing canonical work; no duplicate implementation issues |
| 3 | Contract owner #103; dispatch owner #78 | Map requested fields to existing contracts; identify only real missing fields |
| 4 | Coordinator and provider | Record one accepted external-provider assignment with disjoint paths and branch |
| 5 | Provider owner | Publish the smallest shared increment with exact-source tests and failure cases |
| 6 | Independent B01 owner | Verify provider source and affected contract evidence through the existing gate |
| 7 | Consumer owner | Pin the provider and prove actual useful output, incompatible-source rejection and unchanged replay |
| 8 | #24/#78 owners | Derive a scoped next-action view from canonical records; one eligible choice or an explicit blocker |
| 9 | #134 owner | Project the same issues into scoped queue/review views; dry-run precise effects first |
| 10 | #134 plus independent verifier | Exercise unchanged repeat, unrelated repository movement, board drift and ambiguous response; no accidental writes |
| 11 | Coordinator | Integrate accepted dependencies in order, verify main and retire branch references without losing remaining tasks |
| 12 | #136 | Record a complete request → provider result → consumer verification → queue advancement cycle; select the next useful outcome |

The project horizon remains at least 25 concrete future actions in #136. Do not copy that entire horizon into every branch. Shared acceptance/queue work should consume a limited, explicit lane while the useful domain outcome continues.

## Acceptance, measures and rollout limits

Before claiming this pattern operational, demonstrate:

- One issue identity visible in global and scoped queues without duplicate tasks or contradictory completion state.
- Two scoped workers with disjoint actual writes; an overlapping claim is rejected or explicitly transferred before writing.
- One shared provider used by two consumers, or one real consumer plus a second independently verified reuse case before expanding the abstraction.
- A provider pin change invalidates only relevant consumer evidence; missing, incompatible or unverified inputs block the dependent action.
- Wrong branch/head, stale claim, duplicate delivery, missing acceptance and dependency-cycle cases fail closed.
- A private-board preview names exact effects; unchanged repeats cause no writes; unrelated field values and privacy remain intact. A concurrency change stops and is reported.
- A result survives branch merge/deletion through its canonical issue and immutable evidence. A worker disappearance returns work to an explicit recoverable state, not silent reassignment.
- One useful deliverable reaches independent acceptance and the queue selects its next eligible action. No hosted operation is inferred from an offline test.

Measure time to first useful output, time to accepted output, API calls, blocked/retry time, rework and number of verified consumers. Distinguish elapsed waiting from active work. Use current records; do not create a metrics service. Compare before/after only when measurements are comparable.

Start manually with canonical checklists, existing views and finite worker packets. Add automation only for observed friction. Defer separate branch Projects, autonomous multi-host dispatch, new lease infrastructure and broad lifecycle/schema redesign. If the pilot does not reduce coordination/rework while preserving correctness, keep the canonical issues and remove the extra projection; do not migrate or delete source history.

## Next action and evidence limits

Next: reconcile this proposal with #136 and instantiate the smallest #217/#219 provider-consumer checklist using their existing owners. Any code change is a separately scoped implementation task on the appropriate owner branch.

This branch contains a reviewed-by-author planning document only. No independent review, runtime implementation, worker launch, private-board mutation or performance improvement is claimed. Links and reuse paths were checked against the recorded base; current owner availability, unresolved external gates and runtime capacity must be verified at assignment time.
