# _BASKET — Worker Task, Resolution & Evidence Protocol

**Contract version:** `basket.worker_task@1`, `basket.worker_resolution@1`, `basket.github_evidence@1`. **Owner:** B00. **Version policy:** `architecture/VERSIONING.md` and `architecture/version-manifest.json`; declarations are not release evidence.

## Why

A GitHub issue and a draft PR do not prove implementation is complete, nor do a worker's final chat message or a passing isolated test prove main is integrated. This versioned protocol standardizes **claim → evidence → evaluation → integration**, with falsifiable status gates.

## Sources of truth

1. **GitHub actual state**: issue number + state, branch, PR changed paths and head SHA, CI run conclusion at a specific SHA, main SHA, and explicitly authorized merge. B00 must retrieve these from current GitHub; a manually saved evidence snapshot is historical.
2. **Worker task claim**: one versioned JSON object (`basket.worker_task@1`) in the worker issue, naming issue, spark, problem-scoped branch originally based on main, exclusive paths, dependencies, acceptance criteria and required proof classes. Reuse a suitable existing intake issue when it becomes the canonical worker task; link separate source or receiver issues when needed. A new chat alone creates neither a new task nor a branch.
3. **Worker resolution**: one versioned JSON object (`basket.worker_resolution@1`) as the **last substantive GitHub issue comment or PR comment**, plus a short human-readable final message linking to it. Report a provisional/unknown state rather than fabricating a passed test or publication timestamp.
4. **Orchestrator decision**: B00 reads both worker payload and independently fetched GitHub evidence, runs offline evaluation (where possible) and records assessment as a GitHub issue/PR comment. Worker reports are **not** authoritative for merge/readiness without B00 evidence checks.

Do not commit a continually mutable central worker-status file as authoritative truth. Commit only versioned protocol/code, immutable historical evidence fixtures and an optional dated audit note. The next launch queue is derived from live issues/PRs, not from stale chat summaries.

## State model (separate implementation and integration)

- `claimed`: the canonical worker issue, exclusive assignment and problem-scoped main-based branch exist; a receiving worker has explicitly claimed them.
- `building`: branch has domain-owned changes, no accepted integration proof.
- `review`: worker opened draft PR with test/evidence claims.
- `component_verified`: all task-mandatory acceptance criteria have citations and branch/PR-head checks passed (if applicable), **not merged**.
- `integration_blocked`: tests/PR exist but dependency or baseline branch prevents integration.
- `integrated`: approved PR merged; independently check main CI, branch/release versions and impacted schemas. **Merged ≠ green main CI**.
- `closed`: GitHub issue closed after B00 checks accepted integration disposition; may be closed as `not_planned` if cancelled, but never mislabel as implemented.
- `withdrawn`: cancelled/superseded with written reason. Underlying evidence remains append-only.

A worker may be `component_verified` and `integration_blocked` in different dimensions. A green branch workflow is not a GA release. Keep finance data freshness independent from task-state recency.

## Work routing, continuity and queue

Follow the shared [work-routing policy](../AGENTS.md#work-routing-policy). Read-only work requires no new issue or branch merely because it starts a chat. Routine capture uses an existing authorized writer/storage contract. Repository-content changes, new writers and ingestion-contract changes require a scoped engineering claim before writing.

GitHub Issues are the working queue, with issue #136 as the project index. `orchestration/planner/queue.json` holds reusable planned objectives, not authoritative live status. A `T-006` entry does not imply that a worker exists. Use one canonical issue and `task_id` such as `B21-17` per coherent problem, optionally retaining `task_queue_id: "T-006"`. Resume the knowledgeable owner and feature branch when the problem continues. Reuse a matching unclaimed intake issue before opening another issue. Create a distinct issue/branch for unrelated work, not merely because the conversation changed.

Record any controller-approved owner transfer with source head, remaining obligations, exact paths and exclusive writer before resuming. Never take over from a stale status. Task recipes and capability profiles are reusable; they cannot expand scope. Ordinary authorized work continues without repeated NEXT prompts or new permission requests.

Run the existing planner with `--active` only for independently confirmed workers. If activity is unknown, report it unknown and do not infer it from open PRs. The historical fixture cannot establish live capacity. The planner's old conversation-launch wording is not authority to duplicate the canonical issue. See [planner guide](planner/README.md).

## Minimum task claim

Post a fenced JSON object in the canonical **worker issue** matching `schemas/worker-task.v1.json`: `schema`, `task_id` (e.g. `B05-8`), `spark_id`, `issue`, `branch`, `objective`, `write_paths`, `acceptance`, `dependencies`, `claimed_at`, `state`. Use `null` rather than inventing an unknown claim timestamp. Stable criteria `A1`, `A2` identify independently testable acceptance conditions.

Full example: [B05 task](examples/B05.task.json).

## Required final worker response payload

Post the complete object matching `schemas/worker-resolution.v1.json` to the canonical issue or PR. Give the user a concise summary and a link to that payload. If publication is blocked, provide the complete payload as a file and state that it was not posted. Required fields:

```text
schema, task_id, spark_id, issue, branch, pr, reported_at,
disposition, changed_paths, checks, acceptance, blockers,
handoffs, unknowns, next_action
```

- `checks[]`: test/CI kind, execution mode, result (`pass`, `fail`, `skipped`, `not_run`), evidence URLs and revision. A green CI run must be tied to the exact PR head SHA; skipped checks must not count as passes.
- `acceptance[]`: stable task criterion ID and `pass|fail|not_verified`; evidence required for pass. `component_verified` requires every *mandatory* criterion to pass.
- `blockers[]`: named outstanding issue/PR/provider/CI, whether truly blocking; do not conflate release blockers with nonblocking long-term research.
- `handoffs[]`: issue number, receiver spark and status (`requested`, `claimed`, `accepted`, `completed`, `superseded`).
- `claims[]`: if provided, separate sourced facts, issuer statements, third-party claims, inferences, scenarios and unknowns. Retain point-in-time source availability as known, and never convert a reported private-equity-perpetual mark into a company transaction.
- `unknowns[]`: exact missing tests/coverage; explicit unresolved states are valid.
- `next_action`: ONE specific next owner/action, not a generic “continue work.”

A worker can mark its **conversation** reporting cycle complete while leaving its GitHub implementation issue open and its PR in draft. Prefer truthful `in_progress`/ `integration_blocked` over inflated “resolved” claims.

Full example: [B05 resolution](examples/B05.resolution.json).

## Orchestrator evidence reconciliation

1. Fetch the worker issue and issue/PR changed files from GitHub. Confirm task ID issue number, branch is bound to the canonical issue, the current owner/transfer is recorded, and PR targets main.
2. Fetch the latest PR SHA and its CI runs; preserve timestamps and URL. Compare every proposed `changed_paths` against **actual PR files** and the spark's exclusive write patterns.
3. Verify that any claimed passing workflow is a successful run on the **same current PR head SHA**. Do not count a passing result from an older commit or a different worker.
4. Reconcile every source obligation to implementation, an explicit handoff, a reasoned deferral or a blocker. Structural validation does not establish semantic completeness. Compare task criteria against resolution evidence; missing or failed criteria block `component_verified` readiness. Manually reviewed citations remain labelled as manually reviewed.
5. Determine if the PR merged. Only a separate green main CI run after merge supports integrated validation. No merges, auto-merge, tags, releases or deployments without explicit authorization for that action.
6. Return computed result, unresolved gate IDs and next action. Produce no trading or portfolio conclusions from the worker status metadata.

Offline command:
```bash
python orchestration/worker_protocol.py \
  --task orchestration/examples/B05.task.json \
  --resolution orchestration/examples/B05.resolution.json \
  --evidence orchestration/examples/github-evidence-2026-10-16.json
python -m unittest discover -s orchestration/tests -p 'test_*.py' -v
```
Dependencies: `jsonschema>=4.23`. The example evidence snapshot is **dated 2026-10-16** and deliberately immutable; it is not a live GitHub connector. On each new assessment, B00 gathers an updated snapshot before drawing conclusions.

## Coordination, handoff receipts and maturation

- Begin with one implementation lane and targeted independent verification. Scale only with confirmed capacity, disjoint scope and demonstrated coordination, not historical worker counts.
- Check live assignments and actual PR changed files, including subtree/glob overlap. Narrow, sequence or record a transfer before competing writes. Shared spark membership does not establish exclusive ownership.
- Route work to the existing owner issue and the branch worker who understands it. A self-contained handoff includes source obligations, revisions, exact paths, input/output assumptions, acceptance, dependencies, permitted actions and one next step. Create another handoff issue only when no suitable record exists.
- Trace source obligations → handoff → issue/branch/PR IDs → receiver claim → result → independent assessment. Sending a prompt is not a receiving claim. Accepted intake is not implementation completion; preserve `requested`, `claimed`, `accepted` and `completed` distinctions and explain what was accepted.
- Record the source and comparison baseline of every assessment. Revalidate affected evidence when code, contracts, inputs or the baseline changes; preserve still-valid evidence. Always refresh current head/scope and relevant checks before integration. A passing earlier revision is not evidence for changed code.
- Select the next eligible increment from current issue dependencies, consumer value, downstream unlock and cost. Historical integration orders are not current queue priorities. Continue useful independent work while another item is blocked.
- Mature through bounded accepted increments, without a first-release prerequisite. Read-only research can proceed on explicitly incomplete inputs but cannot claim verified operational outputs. A branch handoff does not require merging it.

## Integration governance

B01 owns integration tests and GitHub workflow changes. B00 owns the three protocol schemas under `schemas/**`, this document and `orchestration/worker_protocol.py`. **Do not update .github/workflows/** from B00. Reuse the existing orchestration and integration test jobs before requesting new coverage. Route genuine CI changes to B01's existing intake with exact acceptance and a self-contained prompt.

For CI, use **static checked-in fixtures** for repeatable offline checks; live GitHub connector evidence belongs to orchestrator evaluations, not a fake self-updating repo file. Release manifest/catalog updates require independent version consistency checks.

## Acceptance assessment

Report pass, fail or missing evidence separately for scope compliance, executed tests, source/provenance fidelity, dependencies, reproducibility and reporting completeness. Preserve each mandatory gate; a weighted average cannot erase a failed or unknown gate. For each problem or blocker, compare viable options across benefit, risk, effort/cost, reversibility and downstream unlock. Use evidence-based qualitative scores; mark unknowns and choose the smallest permitted path. Unify proven repeating patterns so new blocks become easier to add. Keep option analysis proportionate and explain the scoring basis. A maturity assessment is neither a predictive probability nor authority to merge.
