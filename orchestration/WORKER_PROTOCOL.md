# _BASKET — Worker Task, Resolution & Evidence Protocol

**Contract version:** `basket.worker_task@1`, `basket.worker_resolution@1`, `basket.github_evidence@1`. **Owner:** B00. **Current core:** 0.4.1 declared; 0.5.0 candidate remains unreleased.

## Why

A GitHub issue and a draft PR do not prove implementation is complete, nor do a worker's final chat message or a passing isolated test prove main is integrated. The four initial workers (B05 #8/PR #10, B01 #9/PR #13, B02 #11/PR #15, B03 #12/PR #14) demonstrated correct file isolation but inconsistent completion reports. This versioned protocol standardizes **claim → evidence → evaluation → integration**, with falsifiable status gates.

## Sources of truth

1. **GitHub actual state**: issue number + state, branch, PR changed paths and head SHA, CI run conclusion at a specific SHA, main SHA, and explicitly authorized merge. B00 must retrieve these from current GitHub; a manually saved evidence snapshot is historical.
2. **Worker task claim**: one versioned JSON object (`basket.worker_task@1`) in the worker issue, naming issue, spark, unique branch from main, exclusive paths, dependencies, acceptance criteria and required proof classes. A handoff issue is separate from the worker issue.
3. **Worker resolution**: one versioned JSON object (`basket.worker_resolution@1`) as the **last substantive GitHub issue comment or PR comment**, plus a short human-readable final message linking to it. Report a provisional/unknown state rather than fabricating a passed test or publication timestamp.
4. **Orchestrator decision**: B00 reads both worker payload and independently fetched GitHub evidence, runs offline evaluation (where possible) and records assessment as a GitHub issue/PR comment. Worker reports are **not** authoritative for merge/readiness without B00 evidence checks.

Do not commit a continually mutable central worker-status file as authoritative truth. Commit only versioned protocol/code, immutable historical evidence fixtures and an optional dated audit note. The next launch queue is derived from live issues/PRs, not from stale chat summaries.

## State model (separate implementation and integration)

- `claimed`: new worker issue and unique main-based branch exist.
- `building`: branch has domain-owned changes, no accepted integration proof.
- `review`: worker opened draft PR with test/evidence claims.
- `component_verified`: all task-mandatory acceptance criteria have citations and branch/PR-head checks passed (if applicable), **not merged**.
- `integration_blocked`: tests/PR exist but dependency or baseline branch prevents integration.
- `integrated`: approved PR merged; independently check main CI, branch/release versions and impacted schemas. **Merged ≠ green main CI**.
- `closed`: GitHub issue closed after B00 checks accepted integration disposition; may be closed as `not_planned` if cancelled, but never mislabel as implemented.
- `withdrawn`: cancelled/superseded with written reason. Underlying evidence remains append-only.

A worker may be `component_verified` and `integration_blocked` in different dimensions. A green branch workflow is not a GA release. Keep finance data freshness independent from task-state recency.

## Planner task vs worker issue task
B00 maintains a reusable plan queue in `orchestration/planner/queue.json`. A queue entry such as `T-006` is a **planned objective** and does not imply a worker conversation exists. When a user starts a new conversation, that chat creates its **own new issue** and issue-bound `task_id` such as `B21-17`; it may optionally record `task_queue_id: "T-006"`. Task recipes and capability profiles are reusable and combinable, but no recipe grants write access outside the assigned spark.

Run `python orchestration/planner.py --live-github --active T-004 --active T-005 --next-worker` only when those active workers are confirmed. If activity is unknown, omit `--active` and the tool refrains from recommending an additional new chat. The historical evidence fixture cannot establish live status. See [planner guide](planner/README.md).

## Minimum task claim

Post a fenced JSON object in the new **worker issue** matching `schemas/worker-task.v1.json`: `schema`, `task_id` (e.g. `B05-8`), `spark_id`, `issue`, `branch`, `objective`, `write_paths`, `acceptance`, `dependencies`, `claimed_at`, `state`. Use `null` rather than inventing an unknown claim timestamp. Stable criteria `A1`, `A2` identify independently testable acceptance conditions.

Full example: [B05 task](examples/B05.task.json).

## Required final worker response payload

Workers must attach an object matching `schemas/worker-resolution.v1.json`. The final ChatGPT message should provide the issue/branch/PR links and a summary, **plus the complete machine-readable JSON** (one fenced block) that can be posted to GitHub. Required fields:

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

1. Fetch the worker issue and issue/PR changed files from GitHub. Confirm task ID issue number, branch belongs to its own new issue, and PR targets main.
2. Fetch the latest PR SHA and its CI runs; preserve timestamps and URL. Compare every proposed `changed_paths` against **actual PR files** and the spark's exclusive write patterns.
3. Verify that any claimed passing workflow is a successful run on the **same current PR head SHA**. Do not count a passing result from an older commit or a different worker.
4. Compare task criteria against resolution evidence; missing or failed criteria block `component_verified` readiness. Manually reviewed citations remain labelled as manually reviewed.
5. Determine if the PR merged. Only a separate green main CI run after merge supports integrated validation. No merges, tags or releases without explicit user approval.
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

## Multi-conversation concurrency and routing

- Start no more than **three active worker development conversations**, raising to five only after merged CI gate reliability is demonstrated. B00 remains the orchestrator; “active” means still modifying branch code, not a fully handed-off reporting cycle.
- One domain owner per file at any given time. After a task ends, a new same-domain worker needs a **new issue and unique branch**; it does not inherit another chat's branch.
- A downstream request (for example B03→B05 #16, ownership/NAV double-counting) becomes a **new scoped B05 worker objective**, not scope creep on the completed schema-only PR #10. B00 can bundle compatible new requests only if path ownership and dependencies permit.
- First integration objective: review B05 PR #10 (component CI passed); then orchestration PR #2; then B01 PR #13 refreshed to main, with its regression/version validations all running; then independently recheck B02 #15 and B03 #14.
- B02 and B03 remain incomplete with unit-test replay and source-coverage gaps. Neither PR is release-ready just because it exists.
- After integration, prioritize **B21 narrative falsification** and **B06 descriptive traversal** only when upstream event/FX history contracts are adequately validated. Company research can run independently but cannot assert live NAV.

## Integration governance

B01 owns integration tests and GitHub workflow changes. B00 owns the three protocol schemas under `schemas/**`, this document and `orchestration/worker_protocol.py`. **Do not update .github/workflows/** from B00. Use a B01 handoff issue and ready-to-paste prompt to add:
```bash
python -m unittest discover -s orchestration/tests -p 'test_*.py' -v
python orchestration/worker_protocol.py --task ... --resolution ... --evidence ...
```
For CI, use **static checked-in fixtures** for repeatable offline checks; live GitHub connector evidence belongs to orchestrator evaluations, not a fake self-updating repo file. Release manifest/catalog updates require independent version consistency checks.

## Evaluation scoring

Score separately and with traceable evidence:
- Scope compliance (20%): changed paths vs issue and registered spark.
- Test evidence (25%): independently run and SHA-aligned; skipped checks not success.
- Source/provenance fidelity (20%): direct source classes, dates, immutability and no fabricated live status.
- Dependency discipline (15%): handoffs named and blocked/unblocked appropriately.
- Reproducibility (10%): deterministic inputs, tests and version/snapshot identity.
- Reporting clarity (10%): machine-readable payload, unknowns, precise next action.

A weighted score describes **review maturity**, never a predictive probability or authorization to merge. Show missing/evidence gaps rather than awarding false precision.
