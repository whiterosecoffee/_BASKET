# B01 OpenAI integrity worker

Scope: independent offline OpenAI research validation, parent B00. Original #45/PR46 integrated the gate; #66/PR67 repaired old-source acceptance checkout. Successor #64 owns this contract and additional evidence checks on `work/64-b01-openai-worker-contract`. PR URL is recorded on #64 rather than guessed in source.

## Ownership and purpose

Writable: `.github/workflows/openai-research.yml`, `tests/integration/openai_gate.py`, `test_openai_gate.py`, and this document. Existing independent acceptance is consumed read-only. Prohibited: B13 `research/OPENAI/**`, canonical tickers, B00 orchestration/schemas/architecture, B02 runtime/FX and other B01 reservations including `validate.yml`.

Output is reproducible pass/fail evidence, not a valuation, market feed, task scheduler or financial store. Success requires real nonempty unskipped tests, matching checkout revisions, unchanged inputs and exact-head CI. Source failures, missing inputs, skipped/empty suites, timeout, mutation or absent artifacts fail the gate. Passing CI does not establish source truth, live entitlement, deployment, fair value or SFTBY net NAV.

## Interfaces and lifecycle

Reuse `basket.worker_task@1` and `basket.worker_resolution@1` in #64, plus B00's worker protocol. User lifecycle terms map to canonical vocabulary: available is an unclaimed proposal (no new state); claimed -> `claimed`; implementing/testing -> task `building`; review-ready -> task `review` and evidence-backed resolution `component_verified`; dependency blocked -> `integration_blocked`; integrated -> `integrated` only after merge and verified main CI; retired -> reporting ends, with `closed` only under the worker protocol. Do not introduce these descriptive terms into schema enums.

Inputs: actual research head selected by the workflow; exact acceptance/workflow SHA via `github.workflow_sha`; B13 policy/news/source files and tests; B01 independent assertions. Schemas remain B13 research contracts and existing B00 shared interfaces. Provider APIs and entitlements are not needed for offline execution. B13 owns source/classification corrections; B00 owns production interfaces; B04/B09 consume accepted contracts downstream.

The workflow preserves #67's separate `gate`, `acceptance` and `source` checkouts. Explicit manual 40-character source revision is supported; otherwise actual research head is used when present. The documented fallback is an **unmerged dependency only**, never proof that main contains B13. Acceptance always comes from the workflow revision, not an older research branch. Revisions are checked before processing. Missing source files cannot count as passes.

## Method and recovery

| Stage | Input/output and truth | Validation/evidence | Retry/checkpoint |
| --- | --- | --- | --- |
| Discover | GitHub issue, head and changed paths -> scoped claim | refresh relevant ownership; no inferred chat activity | no writes through collision; #64 stores checkpoint |
| Acquire/normalize | Git checkouts -> exact immutable source and acceptance revisions | full SHA assertions; no provider polling or invented timestamps | refetch only after a changed revision/error diagnosis |
| Verify/reconcile | file bytes -> SHA-256 manifests | reject dirty tracked inputs, empty directories and symlinks | `openai-inputs-before.json` within this run |
| Calculate | checker, audit, source suite, acceptance -> real exits/logs | source suite requires >0 executed cases, no skips/expected failures; 120-second suite limit; existing acceptance still fail-closed | independent workflow steps continue after failure; no automatic retry |
| Persist/validate | after-manifest + CI logs -> run artifact | before/after exact equality; additions/deletions/revisions invalidate | artifact keyed by run ID/attempt; no reuse of a prior green run |
| Publish/invalidate | exact CI/source/acceptance revisions -> worker resolution | B00 retrieves actual evidence independently | rerun when input fingerprint changes; no downstream scheduling implementation |

Dependency fingerprint is a deterministic SHA-256 of source/acceptance revision, file-content hashes and Python runtime. Paths inside manifests are relative; cache files are excluded. It is not a canonical financial observation ID or new shared schema. Source/acceptance changes invalidate the result even if another worker did not run. Artifacts preserve the before/after inputs; test outcomes remain in GitHub job/step logs. Artifact retention follows GitHub settings; these are not permanent canonical records. Report URLs/SHAs in the issue for durable lookup.

Run source checks through the workflow or locally with its exact two checkouts. Commands:

```sh
python -m unittest discover -s tests/integration -p 'test_openai_gate.py' -v
python -m unittest discover -s tests/integration -p 'test_openai_workflow_hotfix.py' -v
python acceptance/tests/integration/openai_gate.py snapshot --source source --acceptance acceptance --source-sha "$SOURCE_SHA" --acceptance-sha "$ACCEPTANCE_SHA" --output before.json
cd source
python research/OPENAI/check.py --validate --self-test
python research/OPENAI/resource_audit.py --as-of 2026-10-17
python ../acceptance/tests/integration/openai_gate.py suite research/OPENAI 'test_*.py'
```

The audit date is the existing historical fixture cutoff, not today's market date. Preserve originals and all failed run links. Restart from clean exact checkouts; recompute every check rather than adopting partial success. Mutation errors require investigation/correction by the producing owner. Cancellation is not success. A timed-out source suite fails without retry; the existing 10-minute job limit bounds the complete run. Source-provider or credential work belongs to its owner, not this worker.

## Failure register and acceptance

| Failure | Reproduction/prevention | Evidence |
| --- | --- | --- |
| eager eligible-stage KeyError | original IPO `gate['required']`; fixed by B13 | #45 historical failures and #31 repair |
| old research ref lacks acceptance | do not use `gate/tests` for independent suite | #66/#67; seven existing hotfix regressions retained |
| zero/skipped source cases yield green unittest | reject empty, skips and expected failures | `test_openai_gate.py` subprocess fixtures |
| stale checkout or changed inputs | revision check and before/after hashes; no fallback from failure | stale/mutation/addition/removal/symlink tests |
| hung source suite | 120-second child timeout; no automatic retry | mocked timeout regression |

Acceptance A1 is this operating contract/runbook and existing canonical lifecycle reuse. A2 is the runner's negative tests plus artifact fingerprints; A3 requires actual head CI, including unchanged shared stores/worker QC. Exact results belong to #64, not mutable completion claims in this document. Helpers do not sandbox malicious source, prevent a mutate-and-restore attack, prove entitlement, or enforce branch protection. Those are outside this small integrity component.

Next queue: (1) review this scoped PR and exact CI; (2) authorized integration + main CI; (3) B13 owner integrates reviewed research, after which actual-head source mode is exercised. Production #29 -> #30 -> #28 is separate. Optional future test-runner consolidation belongs to B00 contract review; do not build a parallel scheduler or broaden this issue.
