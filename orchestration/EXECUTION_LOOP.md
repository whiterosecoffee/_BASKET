# _BASKET — Automated Execution and Quality-Control Loop

**Purpose:** B00 selects an outcome-level milestone; deterministic runner decomposes it into bounded tasks, executes available automatable checks, verifies evidence, requeues failures and escalates only permissions/unknowns. This is a controller design, **not a claim that an always-running agent exists**.

## Hierarchy

1. **Outcome**: e.g. SFTBY reliable USD intelligence, measurable acceptance.
2. **Milestone**: e.g. strict canonical relationships validated on main.
3. **Task**: a GitHub issue and one-domain-owned PR, with concrete expected artifacts and tests.
4. **Step**: pure scripted action or constrained worker activity, reusable from `worker-library.json`.
5. **Check**: automatic schema, unit, source, lineage, freshness or CI assertion with exact SHA.
6. **Disposition**: accepted, rework, blocked, queued for approval; each transitions once with an evidence record.

Do not create a new ChatGPT conversation for every step. Code-based subtasks and QC should run in CI and scripts; a new conversation is needed only for domain judgment or changes beyond the current worker's bounded objective.

## Deterministic loop

```text
READ CURRENT GITHUB STATE
    ↓
RECONCILE outcome → milestones → tasks → steps
    ↓
SELECT lowest-unblocked highest-value task within worker capacity and ownership
    ↓
DISPATCH pure automatic steps (validation/replay/verification) or prepare worker brief
    ↓
EXECUTE on owned branch (never main)
    ↓
QC: contract + unit + negative + provenance + regression + CI SHA
    ├── PASS → review and explicit approval gate for merge/tag
    ├── FAIL → add exact failure to same task; return to owner with retry budget
    └── MISSING EVIDENCE → blocked with evidence request, not pass
    ↓
AFTER AUTHORIZED MERGE: independent MAIN CI verification
    ↓
MARK milestone integrated; release next dependent task
    ↺
```

The workflow is **pull based**: B00 or a configured GitHub Action invokes a deterministic reconciliation pass. A persistent event-driven runner could be added later, after permission and sandbox design. GitHub Actions can automate tests and status annotations but cannot open ChatGPT conversations.

## Seven quality gates

- **Q0 Claim**: new issue + unique branch, bounded domain paths and acceptance IDs.
- **Q1 Static**: schema validation, paths, dependency DAG and reproducible task format.
- **Q2 Behavioral**: successful domain unit tests and negative tests.
- **Q3 Evidence**: primary references, point-in-time dates, original units/FX and audit lineage.
- **Q4 Independent**: B01 or CI verifies exact PR head SHA, required checks all pass, none missing/skipped.
- **Q5 Approval**: code review, explicitly authorized merge (not automated).
- **Q6 Integrated**: merged commit, main CI, replay reproducibility and release status.

QC failures loop into the original issue/task; never spawn a new conversation just because a test failed. Escalate only when the failure crosses a domain's owned paths or needs a new authorization.

## Controller invariants

- One task has at most one active **code-writing owner claim**. Reusable capabilities never confer ownership.
- No duplicate issue/branch if the original conversation can continue its task.
- A failing CI run never marks complete; a skipped check never counts as passed.
- Failed/retried operations are idempotent and bounded; retry exhaustion becomes `blocked`.
- The reason for each transition is an evidence-backed observation, not a worker narrative.
- Distinguish **technical readiness** from **authorization readiness**.
- A successful reviewed PR is not the same as green integrated main or production readiness.
- Maintain *one explicit next action* per blocked task and one owner.

## First-cycle application

```text
M0 Repair strict SFTBY schema
  T-001 Review B05 PR #10 → approval → merge → main CI
M1 Make the orchestrator executable
  T-002 Validate B00 PR #2, protocols and planner → approval → merge
M2 Make QC universal
  T-003 B01 PR #13 integration + version/planner/worker tests → green main
M3 Validate two reusable evidence producers (parallel under active-worker cap)
  T-004 B02 market/FX replay and QC
  T-005 B03 source/event revisions and QC
M4 Reuse tested inputs
  T-006 B21 claims/falsification
  T-007 B06 traversal after B02 accepted
  T-008 B05 accounting reconciliation after B03 accepted
```

**B00 review cadence:** invoke reconcile after every substantive PR or CI change, and before a new worker launch. Automated periodic reconciliation can be scheduled separately, but is not currently running. Do not invent completion dates or predictive success probabilities.

## Next implementation boundary

B00 owns this controller specification and orchestration-state evaluator. **B01** must add CI workflow execution after PR #2 reaches main (handoff #6). Optional future deployment/retry queue belongs to B08 and should be justified only after the local controller proves useful. No automatic merging, no off-domain writes.
