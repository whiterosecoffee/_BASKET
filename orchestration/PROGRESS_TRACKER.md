# Planner, progress and queue projection

The existing planner now exposes exact-head workflow findings, optional token/reuse estimates and declared-budget guards. `progress_tracker.py` adds a repeatable read-only view of GitHub issue checklists and planned work. GitHub remains the ledger; these commands neither store a second task database nor launch workers, mutate issues, merge or deploy.

## Use

From the repository root:

```sh
# Explicit historical fixture; not live state.
python orchestration/progress_tracker.py --format json

# Fresh evidence, including open work absent from the legacy queue.
python orchestration/progress_tracker.py --live-github --discover-open --focus-issue 136

# Known planning allowance, not a claim about the subscription balance.
python orchestration/planner.py --live-github --token-budget 4000
```

Existing `GITHUB_TOKEN` support is reused. Do not put credentials in files, output or arguments. Without live mode, the report names the fixture capture mode/time. Failed collection is an explicit error; no silent cached fallback. Discovery and per-head run pagination can require many reads; use a fresh captured snapshot for repeat analysis instead of recollecting unchanged data unnecessarily. API failures/rate limits return an error for retry after recovery, not fake success.

## Decisions and evidence

Input contracts reuse the existing task-queue, worker-library and worker-evidence schemas. The new output contract is `basket.progress_report@1` in `schemas/progress-report.v1.json`, covering success and structured error results; input and output validation run on every report. The outer report and checklist/check findings are strict. Ordered-task records preserve legacy descriptive fields while enforcing the new readiness/check/resource fields. No report may claim verified acceptance or integration readiness from this projection alone.

- The latest run for **each required workflow at the exact SHA** determines PASS/FAIL/PENDING/NOT_RUN/UNKNOWN. A newer failure or pending rerun invalidates an older success. Skipped/neutral is UNKNOWN, never PASS.
- `required_workflows` is optional and defaults to the existing validator workflow. Explicitly configure applicable domain workflows; default generic CI does not establish domain acceptance.
- Draft PRs never become integration-ready in the progress report. Review eligibility, worker acceptance, main integration and runtime deployment are distinct. The tracker does not manufacture missing review or acceptance evidence.
- The legacy planner phase names remain for caller compatibility. In particular, `integrated_main_ci_verified` is **not** proof that this tracker checked all worker criteria, reviews, merge ancestry or deployment. Progress output retains NOT_VERIFIED acceptance and UNKNOWN review requirements until the existing worker-protocol evaluator supplies applicable evidence.
- Open issues absent from the configured task plan are exposed explicitly. Discovery does not silently assign them owners or invent priorities.
- Checklists are reported as recorded progress, not verified completion. Historical `<details>` and fenced examples are ignored. Explicit IDs such as `S01` retain identity across title/status corrections; conflicting duplicates are errors. Items without IDs use text hashes and change identity when renamed. Reprocessing unchanged input has no mutations or additional task creation.

## Optional queue metadata

Existing queue entries remain valid. A task may add:

```json
{
  "required_workflows": ["Validate BASKET data", "Independent component acceptance"],
  "token_estimate": {
    "min": 1000, "max": 2000, "confidence": "low",
    "basis": "Illustrative forecast; replace with evidence for the actual task"
  },
  "reuse_estimate": {
    "tokens_saved_per_use": 300, "expected_uses": 10,
    "basis": "Illustrative reuse hypothesis, not measured savings"
  }
}
```

These values are examples, not registered forecasts. Schema validation plus planner validation check field types and valid min/max ordering. Without estimates, expected savings remain unknown. With a declared budget, missing estimates or a maximum exceeding the allowance prevent new-worker selection. This does not require stopping independent analysis or asking the user for routine permission. With unknown budget, the tool reports `budget_unknown`, never invents quota, and preserves legacy advisory behavior; it still never dispatches workers itself.

The estimated net token reduction is `savings per use * expected uses - maximum initial estimate`. This is an explicitly conditional forecast. It is only a tie-breaker after existing priority/readiness ordering; no PR #25 queue contents or scoring policy were silently replaced. Actual remaining quota is always null unless a future supported measurement is added.

## Tests and limits

```sh
python -m unittest discover -s orchestration/tests -p 'test_planner_maturity.py' -v
python -m unittest discover -s orchestration/tests -p 'test_*.py' -v
```

New regressions cover newer CI failures, pending reruns, required workflows, stale heads, conservative budgets, unknown estimates, forecast validation, draft PRs, source checklist filtering, duplicate/corrected/conflicting identities, resume, unplanned issues, pagination and explicit failure. Existing tests are unchanged.

This increment is operational reporting/planning code, not continuous conversation capture, a connected paid-agent executor or autonomous integration. Existing `worker_task`, `worker_resolution`, controller scope assignments and independent verification remain the integration points. New input/output fields are backward-compatible optional additions to existing schemas; no replacement worker protocol is introduced.
