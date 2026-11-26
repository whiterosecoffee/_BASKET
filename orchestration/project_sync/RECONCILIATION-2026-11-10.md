# Existing Projects adapter: bounded continuation, 2026-11-10

Issue #134 / draft PR #135 remains the sole Projects synchronization workstream.
This is not a second queue, new worker tracker, merge, deployment or release.

## Decisions and preserved benefits

The user authorized progress and treating old machine-generated restrictions as
guidelines whose benefits must be preserved. The original branch and all existing
history are retained. Publication is conditional on the expected previous head
`248987cdd472df42f893c146a5dd1f621e97b8b3`; a moved head requires re-reading before
any ref update. No force update is needed.

Option assessment uses judgment scores from 1 (poor) to 5 (strong), not measured
performance. Dimensions: conflict safety, downstream progress, reuse, simplicity.

| Option | Safety | Progress | Reuse | Simplicity | Decision |
|---|---:|---:|---:|---:|---|
| Wait for PR #25 to reconcile this branch | 5 | 1 | 3 | 4 | Does not clear the current branch's known failure |
| Recompute only this branch's generated scope metadata | 4 | 5 | 5 | 5 | Selected; preserve #25's branch and queue |
| Replace GitHub's existing Status option IDs | 1 | 4 | 2 | 3 | Reject; risks board history and references |
| Explicit native Status mapping plus detailed Workflow State | 5 | 4 | 5 | 4 | Selected; additive, reversible and tested |
| Start another tracker or scheduler | 2 | 2 | 1 | 1 | Reject; fragments the canonical queue |

## Changes

- Reconcile catalog version 1.6.1 and add the already-owned `copier.yml` path to
  T-001/T-002 generated scopes. Preserve all queue entries, recipes, acceptance
  criteria and strict validators. PR #25 still requires its own eventual source
  reconciliation; its branch is not modified by this correction.
- Explicit `--native-status` mode preserves GitHub's Todo/In Progress/Done option
  IDs and retains the full lifecycle in Workflow State. No readiness/completion
  inference is added. BLOCKED/FAILED/cancelled remain distinguishable there.
- Preflight incompatible field types/options and duplicate names before creating
  any fields. Missing fields in dry-run use synthetic metadata solely for planning
  dependent writes, never mutation credentials or persisted GitHub identities.
- Emit mode-correct, unapplied view specifications. Priority remains operator-owned;
  repeated sync does not overwrite a manually selected Priority.
- Keep the existing task identity and record the exact generated-manifest exception.

## Verification

Original source was fetched at the exact old PR head. All 62 materialized baseline
source files matched their Git blob hashes before testing. Original 29 adapter
tests passed. Original orchestration suite ran 57 tests: 56 passed, one failed
with `catalog version mismatch`, `scope paths mismatch T-001`, and `T-002`.
The same failures are recorded in Actions run 41168999169, job 124442675034.

Candidate tests use Python 3.12, jsonschema 4.23.0, PyYAML 6.0.2 and Copier 9.19.1:

- Adapter: 39 tests passed, including ten new regressions.
- Orchestration: 57 tests passed, with the original strict test unchanged.
- Real native Copier copy/update integration: six tests passed.
- Six strict governance validators passed; compileall passed for the adapter.
- Independent review reproduced the old failure and candidate results. It found
  fresh-board dry-run and mode-specific-view gaps; both were fixed and retested.

See `TEST_RESULTS-2026-11-10.txt` for actual local runner output. Local materialization
initially omitted documentation required by validate_versions; after fetching the
unchanged exact-head files, that validator passed. This was not a repository defect.
No ticker-store validation or independent cross-domain integration suite is claimed
for this partial local materialization. Exact-head Actions remains separate evidence.

## Remaining acceptance

`gh project list --owner whiterosecoffee --format json --limit 100` returned exit 4
because this executor has no GitHub CLI login. The repository connector has no
Projects endpoint. No live Project was discovered or changed, no credentials were
handled, and no permission denial was bypassed. Live URL/ID, field/view behavior,
idempotent imports and a real work/verification/next-item cycle remain unverified.

The standard workflow does not run adapter or Copier tests. B01's existing handoff
on #134 must supply independent exact-head execution and eventually approved CI
wiring. This change installs no workflow or token-bearing worker.

Closed/merged history, evidence-cleared dependencies, automatic READY/COMPLETE,
priority/rank synchronization and actual view creation remain outside this bounded
increment. Native Project operation can precede additional automation. The reusable
pattern is: inspect existing native identities, preflight compatibility, plan changes,
apply only reviewed deltas, reread, prove idempotency, and keep acceptance distinct
from synchronization and integration.
