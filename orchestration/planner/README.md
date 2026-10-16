# _BASKET — Composable Worker Planner and Task Queue

**Owned by:** B00 · **Registry candidate:** 1.5.0 · **Core baseline:** 0.4.1, unreleased 0.5.0 target.

This is an **operating queue**, not a new set of 22 simultaneous conversations. GitHub issues, PRs, PR file changes and CI runs remain authoritative for execution state. The versioned queue and profiles define desired objectives and execution requirements; they do **not** assert that workers are live or that PRs are integrated.

## Three separable layers

**Task** = one bounded objective, with spark/domain owner, acceptance, priority, effort, source handoffs, dependencies and an execution mode (`orchestrator_review`, `resume_existing_worker`, `launch_new_worker`). The queue is a DAG; each dependency has an explicit gate (`issue_exists`, `ci_passed_on_head`, or `merged`).

**Reusable capability** = a procedure that can be reused across tasks (e.g., `source_audit`, `immutable_replay`, `adversarial_validation`, `github_evidence`, `economic_sensitivity`). Each capability specifies expected artifacts and minimum evidence.

**Worker profile** = a reusable bundle of capabilities, such as `data_engineer`, `evidence_researcher`, `qa_reviewer`, or `integration_steward`. A task can compose **several profiles** and a step-by-step recipe. Profile composition is limited to the **ONE assigned spark's** `write_paths` and never authorizes cross-domain modifications.

This differs from keeping one immortal worker per topic: a worker capability can execute on SFTBY, CRWV, AAOI or narrative work **only under the specific task's domain ownership and issue-scoped branch**. When a task ends, its conversation can hand off; a future new conversation creates its own issue+branch even if the same profile/recipe is reused.

## Files

- `worker-library.json`: the reusable capability catalog, six profiles and eight recipes.
- `queue.json`: eight initial project tasks, strict dependencies, mode and profiles.
- `../../schemas/worker-library.v1.json`: strict profile/recipe syntax.
- `../../schemas/task-queue.v1.json`: strict queue syntax.
- `../validate_planner.py`: structural schema + semantic ownership/capability/DAG checks.
- `../planner.py`: deterministic priority/blocked-state calculation and next new-worker prompt.
- `../github_snapshot.py`: **read-only** current GitHub fetch, optional GITHUB_TOKEN; never stores credential or creates/merges anything.
- `../tests/test_planner.py`, `../tests/test_github_snapshot.py`: offline tests.
- `../WORKER_PROTOCOL.md`: task claim and resolution schema; B00 independently verifies current PR SHA and checks.

## Execution

Requires Python 3.10+ and `jsonschema>=4.23` for the structural validation command.

```bash
python orchestration/validate_planner.py
python -m unittest discover -s orchestration/tests -p 'test_*.py' -v

# Reproducible historical fixture, NOT current GitHub status:
python orchestration/planner.py --evidence orchestration/examples/github-evidence-2026-10-16.json \
  --active T-004 --active T-005 --next-worker

# Fresh snapshot from public or authenticated GitHub, NO background process:
python orchestration/planner.py --live-github \
  --active T-004 --active T-005 --next-worker

# Or explicitly declare zero active writing workers if that is true:
python orchestration/planner.py --live-github --assume-none-active --next-worker
```

For private repositories, provide `GITHUB_TOKEN` as an environment variable without printing it in logs. The read-only fetch fails closed on network/rate-limit/response issues. `--active` is a *user/orchestrator-confirmed set of currently code-writing tasks*. A draft PR by itself is insufficient evidence that a conversation is currently running. If worker activity isn't supplied, the planner reports unknown capacity and does **not** recommend launching an additional chat.

**Never equate historical fixture evaluation with live status.** `github-evidence-2026-10-16.json` is marked `reconstructed_fixture` with `observed_at: null` since original collection time was not independently established. Fresh collector outputs use `capture_mode: live_connector` and actual UTC collection time.

## Initial planned work

1. `T-001` — B00 review B05 PR #10; prior strict CI success at exact PR SHA (merge only with explicit authorization).
2. `T-002` — B00 review orchestration PR #2 after B05 integration.
3. `T-003` — B01 combined CI PR #13 after both preceding PRs are merged and baseline contracts available.
4. `T-004` — B02 resume Issue #11/PR #15; complete unit tests and historical FX/replay.
5. `T-005` — B03 resume Issue #12/PR #14; complete source ledger and revision tests.
6. `T-006` — B21 new narrative analysis worker (slot-dependent; new issue and branch required).
7. `T-007` — B06 traversal worker **after B02 foundation merges**.
8. `T-008` — B05 OpenAI graph follow-up #16; **new worker branch** after B03 event integration, no expansion of closed repair PR #10.

This is a **prioritized backlog**, not 8 concurrently operating agents or 8 automatically created branches. B00 integration reviews do not consume the capped code-writing worker slots. Existing incomplete workers should resume their own conversations/branches when accessible; if they are not accessible, start a newly claimed issue and branch with a handoff and re-baseline.

## Scheduling and priority methodology

The planner uses fixed ordering: actionable tasks precede blocked tasks; then priority band P0/P1/P2, impact, estimated effort and the number of downstream dependencies they unblock. This score is solely a **queue-ordering heuristic**. It is neither probability, delivery ETA, economic benefit, nor permission to merge.

Gate semantics are explicit:
- `issue_exists`: recorded upstream worker issue is present. No implication the implementation is complete.
- `ci_passed_on_head`: at least one relevant named workflow succeeded at the exact current PR head SHA. This does **not** certify all acceptance.
- `merged`: GitHub reports the PR merged. A merged PR remains `integrated_main_ci_unverified` until independent main CI evidence is observed.

Existing tasks with an open PR may require more tests or source coverage. Their mode is `resume_existing_worker`, not “done” and not “launch duplicate worker.” Current status is derived from the fetched evidence only.

## Reuse and recombination example

`evidence_researcher + data_engineer + qa_reviewer` on B03's `issuer_ledger` recipe produces issuer sources, immutable revision replay and adversarial deduplication tests. The same `data_engineer + qa_reviewer` is reused under B02's `historical_replay` recipe. A later B21 objective combines `evidence_researcher + inference_analyst` for falsification. **No file ownership crosses B03/B02/B21 boundaries** even though capabilities overlap.

## Maintaining queue truth

- B00 updates `queue.json` as the set of PLANNED objectives changes; it does not continuously overwrite status files.
- At evaluation, fetch GitHub evidence via `--live-github`, inspect current PR changes and pending handoffs, and rerun the planner. If evidence cannot be refreshed, clearly mark the recommendation historical/unknown.
- When starting a new worker, use the output prompt. The new chat creates **one new issue and branch from main**, posts `basket.worker_task@1` and later a complete `basket.worker_resolution@1` with evidence.
- Requeue incomplete work under the same conversation only if its issue/branch still belongs to that conversation. When cross-chat handoff is necessary, create a new issue/branch and link the old evidence.
- B01 integrates `validate_planner.py` and planner tests into CI through handoff #6; B00 does not edit CI workflows.
- No action in these scripts creates an issue, opens a ChatGPT conversation, merges a PR, or schedules persistent background work.
