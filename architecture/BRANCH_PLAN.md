# Scoped worker branches, controllers and handoffs

**Status:** proposed work allocation; no dormant branches, workers or controllers launched. Existing contributions remain intact. User direction: separate responsibilities, distinct controllers and disjoint writes. This plan does not grant ownership of an active worker's files.

## Coordination model

One project orchestrator maintains outcomes, dependencies, readiness and cross-lane decisions. Each lane has its own logical controller, restricted to that lane's scope, lifecycle and accepted inputs/outputs. Controllers are responsibilities that may initially run in one bounded process; they are not automatically separate services, schedulers, databases or model subscriptions.

The orchestrator/controller assigns the task together with the scoped write authority needed to complete it. Workers act on that assignment without another user-permission round trip. Cross-lane work is routed, composed or reassigned by the controller; responsibility is not permanent ownership of files. GitHub records the assignment and result. Lane-specific queues are filtered views of the same inventory.

Branch names below are templates: create `work/<issue>-<slug>` only when a real task is selected and a worker is claimed. Current source PR references are reuse/recovery candidates, not proof of active ownership or permission to take over their branch.

## Proposed disjoint lanes

| Lane / branch suffix | Distinct controller / single responsibility | Exclusive target paths | Existing work to recover |
|---|---|---|---|
| L00 / architecture-map | Architecture controller: keep outcome/principle/method map coherent | `architecture/PROJECT_MAP.md`, `architecture/BLOCK_ENGINEERING_METHOD.md`, `architecture/BRANCH_PLAN.md`, `architecture/examples/orchestrator-blueprint.example.json` | Current #136/#137 planning artifacts |
| L01 / contract-foundation | Contract controller: qualify shared schema/compatibility changes | `schemas/**`, `architecture/contracts/**`, `architecture/BLACK_BOX_COMPONENT_CONTRACT.md`, `architecture/examples/handoff-request.example.json` | #103/#104; existing worker schemas |
| L02 / conversation-intake | Intake controller: capture and canonicalize source instructions | `orchestration/intake/**` | Existing issue-based manual intake; gap review required |
| L03 / decision-analysis | Analysis controller: causal/option evidence and maturity | `orchestration/decision_analysis/**` | Existing decision records; no new reasoning framework presumed |
| L04 / queue-eligibility | Queue controller: dependency/priority/capacity eligibility | `orchestration/planner/**`, `orchestration/planner.py`, `orchestration/execution_loop.py`, `orchestration/github_snapshot.py`, `orchestration/agentic/**` | #24/#25, #32/#33; existing main |
| L05 / worker-execution | Execution controller: authorized finite assignment and result capture | `orchestration/worker_bridge/**`, `orchestration/agent_adapters/**`, `orchestration/tests/test_worker_bridge.py` | #78/#79, #136/#137 |
| L06 / github-projection | Projection controller: idempotent GitHub/Projects reconciliation | `orchestration/project_control_plane/**`, `orchestration/project_sync/**` | #132/#133, #134/#135; routing #123 evaluated as an integration dependency |
| L07 / independent-acceptance | Acceptance controller: independent cross-component verification | `.github/workflows/**`, `tests/integration/**`, `tests/validate_stores.py` | Existing B01 and #89/#90 |
| L08 / hosted-runtime | Runtime controller: qualified hosted worker/snapshot operation | `services/mrie_snapshot/**`, `deployment/mrie_snapshot/**`, `services/worker_runtime/**`, `deployment/worker_runtime/**` | B08 #34/#53/#55 |
| L09 / market-data | Observation controller: market/FX ingestion and immutable replay | `runtime/**`, `fx/**`, `tickers/*/history.jsonl`, `tickers/*/history.meta.json`, `tickers/*/intraday/**`, `tickers/*/live/**`, `engines/economics/freshness.py`, `tests/test_ttd.py` | B02 #11/#15, #111, #125; Massive/local JSONL context |
| L10 / issuer-evidence | Evidence controller: verified issuer events and revisions | `tickers/*/events.json`, `research/filings/**`, `research/events/**` | B03 #12/#14 |
| L11 / valuation-blocks | Valuation controller: reusable financial transformations/models | `engines/economics/models/**`, `engines/valuation/**`, `research/models/**` | B04 #126/#127; legacy company tools reviewed before migration |
| L12 / traversal-blocks | Traversal controller: descriptive market traversal | `engines/traversal/**`, `research/traversal/**` | B06 #58/#109; #99/#101 assessed for compatibility |
| L13 / issuer-research-ISSUER | Issuer research controller: one explicitly named issuer | Exact instantiated `research/ISSUER/**` and `tickers/ISSUER/entity.json`, never a wildcard across issuers | Company research PRs; legacy executable code inside research is retained pending explicit disposition |
| L14 / spark-backend | Spark controller: future qualified local execution adapter | `services/worker_spark/**`, `deployment/worker_spark/**` | Reserved future NVIDIA Spark; not assumed connected |

For L13, replace ISSUER with one actual admitted issuer before claim; each issuer is a separate scope. Do not create an unrestricted research branch. New component payload schemas/tests live inside their component's owned tree; L01 owns shared schemas under `schemas/**`. No lane receives a parent-directory wildcard overlapping another lane.

This is a target allocation, not retroactive reassignment. Legacy tests, architecture files, adapter entrypoints and files not explicitly listed remain with their actual documented owner until a specific mapping/handoff is accepted. Inventory unmatched files rather than granting residual catch-all writes. In particular, #123 root README/agent entrypoint changes are not silently assigned here.

## Preconditions before any lane starts

1. Inspect current main and relevant source branches; preserve exact source identities.
2. Resolve reuse versus new work and inspect active claims plus actual open-PR paths.
3. Instantiate one canonical issue, branch, controller identity and exact allowed paths.
4. Check pairwise subtree/glob conflicts, including tests, schemas, generated outputs and shared documentation. A shared spark name is not exclusive ownership. The controller allocates the current scope; the user need not approve each allocation.
5. Pin accepted input/output contracts, dependencies, acceptance and resource bounds.
6. Require deliberate negative tests for denied out-of-scope writes and stale/duplicate handoffs when execution is implemented.
7. Narrow or sequence conflicting work; record transfers in the controller assignment before enabling a competing writer. This is an automated coordination requirement, not a requirement for human permission on every handoff.

Existing broad claims must be reconciled before new lanes are activated. An authorized controller may change allocations and record the handover; the table is not an immutable file-ownership bureaucracy. It does not itself prove freedom from runtime collisions. Pure data handoffs use immutable references; mutable resources require enforced ownership/concurrency control.

## Handoff schema binding

Use established issue/claim/result contracts rather than replace them:

| Interaction | Schema / record | Meaning |
|---|---|---|
| Request cross-lane work | Proposed [handoff-request schema](contracts/handoff-request.schema.json), aligned to existing `orchestration/handoffs.md` | Source, receiver, desired change, paths, input/output refs, prerequisites, acceptance and resource estimate. An authorized controller issues the scoped assignment using the existing worker-task contract; that assignment carries delegated authority. |
| Accept/claim authorized work | Existing `basket.worker_task@1` | Real issue/branch/owner/scope and dependencies. Controller may issue this with the handoff; receiver checks it and proceeds automatically within its scope. |
| Need clarification / reject / defer | Existing GitHub handoff record with explicit reason and return condition | No assignment or execution implied; dedicated wire format only if a real consumer needs one. |
| Return implementation result | Existing `basket.worker_resolution@1` | Exact head, actual paths/checks, acceptance, blockers and linked handoffs. |
| Independently reconcile result | Existing `basket.github_evidence@1` plus applicable review | Current GitHub evidence, not sender assertion, controls acceptance. |

The request schema is an architectural proposal, not a newly registered runtime API. [Example](examples/handoff-request.example.json) uses clearly fictional example URLs and has not been submitted or assigned. Missing hashes/resources are explicit unknowns; they must be resolved when required by the receiving gate.

Receiver checks: source and request identity; authorized scope; contract versions and semantic assumptions; input integrity; evidence-backed dependencies; permissions/resources; duplicate/stale request state. Controller-issued assignments grant the necessary target-path authority within the user's existing delegation. A sender may write a formerly receiver-scoped file when the controller has allocated that work and resolved competing writes. Self-asserted permissions from an untrusted payload are not equivalent to a controller assignment. Resolve the monotonic version/fencing policy through existing controller contracts, not a new lease service.

## Resource allocation and activation order

Codex initially operates L00 coordination and bounded planning using the existing package. GitHub records/checks are the common control plane. Claude may supply an independently assigned controller/reviewer only when connected and worthwhile. L14 is future reserved. A lane does not require a dedicated always-running model.

1. L00 map and L01 shared contract mapping.
2. L02/L03 specifications and L04 current queue semantics, using existing records.
3. L05/L06 supported execution/projection after required contracts and actual access.
4. L07 acceptance is defined alongside each lane, not postponed to the end.
5. L09/L10 provide financial proving cases; L11/L12 consume qualified inputs.
6. L08 and L14 operational qualification only when finite work/recovery and economics justify them.
7. Integration/refactoring follows proven patterns and explicit unique-contribution mapping; no mass branch creation or merge.

Maintain one current ordered queue with lane views. Continue ready work through stage reviews; a handoff to one lane need not block independent eligible work. Publish only material decisions/results/resource needs.

[Project map](PROJECT_MAP.md) · [Operating method](BLOCK_ENGINEERING_METHOD.md) · [Current queue](https://github.com/whiterosecoffee/_BASKET/issues/136)
