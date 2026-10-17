# Worker job execution, failures and reusable procedural learning

B00 has compiled eight current tasks into `worker-scopes.json`. Each scope carries an exact objective, existing or to-be-created issue/PR identity, owner, permitted write paths, dependencies, repeatable recipe steps, acceptance criteria and completion payload. A reusable worker profile is never an authorization to write outside the assigned spark.

Every attempted step has an append-only logical record in a task-specific `attempts/T-nnn.json` ledger, validated against `schemas/worker-attempts.v1.json` and `orchestration/validate_worker_attempts.py`. Records include attempted procedure, observed result, pass/fail/block, sources, correction, retry chain and measured effort. Failed attempts remain visible. B00 can upgrade a procedural lesson from proposed to adopted only after a successful corrective retry. No hidden model fine-tuning or prompt instruction rewrite is implied.

## Accuracy and efficiency discipline

- A passed attempt needs evidence; a failed attempt needs a concrete resolution or escalation.
- A retry must reference an earlier same-step attempt. Invalid/circular lineage fails validation.
- First-pass rate counts only first attempts; repeated retries do not inflate it.
- Durations/tool counts are numeric only when measured. Unknowns are null; no fabricated productivity gains.
- A task does not become done merely because an attempt passed: evaluate all task acceptance criteria and exact-head CI.
- If a worker needs another spark's code, issue a handoff, not an expanded profile.
- Workers may consume successful lessons from prior similar tasks, but all reused procedures are subjected to the current task's QC, sources and permissions.

The initial `T-001` example documents an actual failure (GitHub rejected merging a draft PR) and a corrective retry (transition to ready-for-review, squash merge pinned to reviewed SHA). Main validation succeeded after merge. This is a reusable *procedure*, not a new economic fact.

## Required iteration

```
Claim task and exact owned files → Execute a recipe step → Record attempt
  → QC checks evidence and correctness
    → FAIL: preserve failure, diagnose, retry same task/step
    → PASS: record versioned evidence, progress to next step
    → UNKNOWN: request source/check, do not claim pass
  → ALL ACCEPTANCE MET → independent PR-head CI → integration
  → MAIN CI → next queued task
```

Commands from repo root (after `jsonschema` is installed for the additional schema validation):

```bash
python orchestration/validate_worker_scopes.py
python orchestration/validate_worker_attempts.py
python -m unittest discover -s orchestration/tests -p 'test_*.py' -v
```

B01 CI implementation is requested in handoff #6. Until executed there, committed code/tests are **not** independently verified.
