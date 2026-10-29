# Successor orchestrator and capability discovery — B00 #59

Issue [#59](https://github.com/whiterosecoffee/_BASKET/issues/59), branch
`work/59-orchestrator-retirement-intake`, draft PR #60. Parent: B00 orchestration.
Exclusive writes: `orchestration/retirement_intake/**`. Everything else is read-only,
including the #25 queue, #33 manager, #49 dispatcher, #79 agent adapters, #104
black-box contracts, B01 CI and all ticker/domain stores. This contract narrows
the B00 spark; it grants no other worker's paths.

## Purpose and existing interfaces

Preserve retirement evidence, discover existing source and separate source presence,
independent acceptance, integration and operation. Reuse `basket.worker_task@1`,
`basket.worker_resolution@1`, `orchestration/github_snapshot.py`, the planner's
worker-library, the #33 manager and #49 dispatcher. The worker library describes
procedural capabilities/recipes; this dated index links actual implementations.
PR #104 owns the proposed component manifest schema: do not introduce another
black-box schema here. This tool is a read-only discovery/cache utility, not a
manager, scheduler, canonical market store, dispatch authorization or live registry.

Inputs: source-pinned GitHub main tree, full open issue/PR/branch inventories,
PR file/blob identities and exact-head workflow evidence. A collector must exhaust
pagination or explicitly reject completeness. The dated evidence file records what
was retrieved; a saved snapshot never verifies current GitHub. Tokens are neither
accepted nor stored by the utility. Unknown versions, invocation, entitlements,
coverage and deployment evidence remain null. README-declared interfaces are
marked as declarations, not independently tested contracts.

Outputs: deterministic JSON discovery report, exact-path collisions, per-component
dependency fingerprints and invalidations relative to an earlier report. A missing
record triggers retrieval; it does not establish absence/merge/deletion. Exact path
comparison does not replace issue scope/glob/semantic ownership review. No PR is
component-verified merely because unrelated shared checks succeeded.

## Runbook

From a complete checkout:

```sh
python -m unittest discover -s orchestration/retirement_intake -p 'test_*.py' -v
python orchestration/retirement_intake/inventory.py --evidence orchestration/retirement_intake/2026-10-29-startup-evidence.json --query CRWV
python orchestration/retirement_intake/inventory.py --evidence /tmp/fresh-evidence.json --previous orchestration/retirement_intake/2026-10-29-capability-inventory.json --output /tmp/new-revision.json
```

Acquisition uses the connected GitHub read API; `inventory.py` intentionally does
not duplicate the existing GitHub collector. Full timestamped evidence is required;
head/file/CI changes invalidate its digest. Cache reuse additionally requires an
explicit age limit (default five minutes); future timestamps fail reuse. A new
snapshot can be rendered without pretending it is fresh. Never overwrite an old
report: use a new revision name. No scheduling/retry process is installed. Failed
acquisition preserves the last snapshot as historical and blocks fresh claims;
retry acquisition only after correcting pagination/auth/connectivity evidence.

## Lifecycle and acceptance

Requested labels map to canonical vocabulary: available = unclaimed proposal,
claimed = `claimed`, implementing/testing = `building`, review-ready = `review`
(or `component_verified` only after all mandatory evidence), blocked =
`integration_blocked`, integrated = `integrated`, retired = `closed` or
`withdrawn` with reason. Runtime/deployed evidence is an independent dimension.

Acceptance: discover source-pinned implementations without cross-owner writes;
reject partial snapshots, stale-head green checks, duplicate PR identities and
unsafe paths; invalidate changed dependencies; retain failures and unknowns;
independent B01 review plus exact-head CI before integration. Success is a reusable
startup path through GitHub; failure is duplicated components or unsupported claims.
No human chat activity estimate is inferred from open PR count.

## Failure register and next execution

The October 18 records retain original failures and their dated corrections. Current
main QC integration supersedes the old M-002-blocked snapshot, without rewriting
history. On October 29 the first local broad test attempt failed to import
`jsonschema`; install the existing workflow's pinned dependencies and rerun, never
weaken the tests. New inventory tests are separate from B01 domain CI until reviewed.

Priorities: (1) existing queue owner #24 refresh #25 against fixed main, reconcile
claimed/completed T-009 and require exact-head checks; (2) B01 independently gate
#33/#49/#104 through existing #65/#105; (3) B02/B03 source/revision producer and
B08 persistent operation through existing handoffs. Domain research can continue
inside current reservations. No new worker is launched by this contract.

Retirement: this orchestrator remains the coordination receiver. It may archive only
with a successor retrieving #59/#60 and refreshing the evidence; committed snapshots
alone are never an autonomous operational service.
