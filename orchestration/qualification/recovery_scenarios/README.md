# Worker recovery qualification (B00-250)

Fifteen JSON-first **simulated** scenarios exercise published main helpers at
`74d913e8913d630d85451344689e093aeea07efc`. `scenarios.json` pins source bytes,
expected transitions, actual helper expectations and explicit gaps.
`test_recovery.py` calls existing helpers; it is not a controller or recovery engine.
`results.json` records actual offline observations, not live worker outcomes.
The #226 design at `10be98031aa5dbd9b5841cc8f88bab5b834790e2` supplies the
simulation-versus-execution distinction; its intake/review model is not copied.

Run from repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s orchestration/qualification/recovery_scenarios -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s orchestration/tests -p 'test_worker_v2_contract.py' -v
```

Actual local result: 19 recovery checks and 17 unchanged worker-contract tests
pass, zero skips/errors/failures on the final run. An initial recovery run had
18 passes and one test-fixture failure: the stale-head mutation selected the
first PR instead of the report's PR. The test was corrected to select by PR
number; the original failure is retained in `results.json`.

## Bounded findings

- An interrupted or merely acknowledged attempt remains pending. A success
  result cannot restart the same attempt or serve as a failed retry parent.
- Repeated identical journal event IDs reject. Unchanged replay returns the
  same output without input mutation. Distinct wake IDs are not a general
  semantic deduplication mechanism.
- Retry ancestry retains prior failures and rejects missing parents and
  changed step identity. Expired leases leave capacity untrusted.
- Stale snapshots, historical operation evidence, wrong PR-head evidence and
  newer failed CI remain rejected. Protocol baseline control passes.
- **Gap:** unknown external-write outcome must be reconciled at the target
  before retry. The unresolved-attempt guard blocks retry, but a caller can
  mark the attempt failed with an arbitrary result URL and then pass ancestry
  checks. The helper does not validate external reconciliation. This case is
  a passing *characterization test*, not accepted recovery behavior.
- **Gap:** `user_steering` is rejected as an unknown event. Current helpers
  do not bind newer instruction revisions to dispatch authorization.
  Re-read current scope and steering before action; owner #32/#78 decides
  the implementation. Rejection alone does not satisfy steering recovery.

The described transitions are qualification expectations, not new canonical
state enums. `attempt_started` is only a proxy for an acknowledged dispatch;
transport receipt reconciliation and persistent completed-result projection
are not tested. No worker was launched, schedule changed, real journal
written, remote operation simulated as successful, or private data included.

Acceptance A1/A2 is bounded to source-backed scenarios and actual helper
observations including explicit gaps. Operational recovery is **not accepted**.
B00 #32/#78 should review the reconciliation and steering gaps before adoption;
#106 retains evidence-gate ownership and #24 planner ownership. This new lane
only owns this directory. Shared CI discovery under `orchestration/tests`
does not execute this folder; focused local results cannot be called hosted
or independent acceptance. No merge is requested by this artifact.
