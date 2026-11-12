# Bounded execution admission — B00 local candidate

Purpose: evaluate an execution request against separately supplied controller pins
and executor observations before a task is eligible for an executor's final
admission check. This module is a pure validator, **not a live launcher**, process
manager, lock service, publication approval, or replacement for existing worker
contracts. It never authorizes effects, including when its decision is eligible.

## Responsibility, scope and authority

Owner: this delegated B00 admission worker. Local task identity:
`local-20261112-execution-admission`. Branch:
`work/local-20261112-execution-admission-portable`, in its own isolated worktree, based on
main `74d913e8913d630d85451344689e093aeea07efc`. The durable local scope manifest is
[task.json](task.json). Exclusive candidate writes: `orchestration/execution_admission/**`.
The parent delegation authorizes this bounded local increment; it does not confer
another owner's authority or bypass publication review.

The initial suggested bootstrap paths were deliberately not used. Current
[#134](https://github.com/whiterosecoffee/_BASKET/issues/134) and
[PR135](https://github.com/whiterosecoffee/_BASKET/pull/135) still own that subtree,
at head `2fbfd085d83cdcdfd264fdd3545339739bf890c8`; previous writer cessation is
unverified. All 77 current open PR path inventories and current open issue claims
were checked on 2026-11-12 before local edits. The new folder has no observed
collision. This is point-in-time evidence, not a complete writer lease.

Automatic approval review rejected creation of a new public task issue. That issue action was not retried. Later user direction authorizes a separate
portable branch publication subject to permission review. This candidate is not
an issue-registered task or admitted live worker; no PR, merge or operational
acceptance is implied. The original local evidence branch is preserved, and this
publication branch begins at current main so private identifiers in local commit
history are not uploaded.

Read-only dependencies: #136 queue/controller, #134 bootstrap, #207 data-worker
continuation, #201/PR209 policy. No modifications to global AGENTS, policy,
catalog, canonical schemas, CI, runtime, market data, or their owner files.

## Contract and usage

Dependency: already installed Python 3.12 / jsonschema 4.26.0 (Draft 2020-12).
No dependency installation or network use is required by this module.

```python
from orchestration.execution_admission.preflight import evaluate

receipt = evaluate(request, observation, controller_pins,
                   now="2026-11-12T12:00:00Z")
```

The request schema's root describes declared task identity/owner/spark, policy
version, purpose/manifest, branch/head/worktree, owned folders, inherited
authority, allowed writes, executor/resources, input schema/hash/freshness,
prerequisites, acceptance tests, permitted effects, recovery/idempotency,
continuation/transfer and parking-only fallback. Its `$defs.observation` and
`$defs.trusted` are reusable, strict schemas for the separate arguments.
`receipt.schema.json` describes the hash-bound result. All objects reject unknown
fields. Required fields cannot silently default to success. The controller pins
bind the authorized task, identity, scope, effects, executor and collector; the
request cannot broaden them. A controller-approved request hash also binds the
complete declared requirements: a worker cannot remove mandatory inputs,
prerequisites, resources or acceptance tests and still receive eligibility.

Concrete repository paths only: slash-separated relative names, no wildcards,
traversal, absolute paths or platform aliases. Folders are subtree roots without
trailing slash; allowed writes may be concrete files or roots. Case-insensitive
ancestor/descendant checks conservatively catch Windows collisions. Unsupported
scope syntax rejects rather than approximating a match. Existing glob scopes
must be concretely resolved by the trusted caller, with complete inventory.

The observation must contain the complete ownership and writer inventory relevant
to the proposed roots **and** branch/worktree. A competing process, even under the
same task identity, is not an additional authorized writer. The trusted collector
must resolve real filesystem paths, symlinks/junctions, worktree isolation and
process identity; opaque `worktree` strings here are pinned identities, not an
implementation of Windows filesystem canonicalization.

New work requires a registered issue-bound branch and independent confirmation
that the task/worktree identity is new. Continuation retains the exact pinned
identity, including branch/head/worktree and owner. A legitimate head advance
requires a newly reconciled controller pin and continuation snapshot; an old
receipt never authorizes a changed head. Replacement requires a recorded transfer
and positive evidence that the previous writer stopped. Transfer does not erase
an active overlapping claim; the caller must reconcile/retire it first.

New launches and transfers reject **every active writer**, including an identical
task/owner/branch/worktree tuple. Continuation requires exactly one active writer
whose `session_id` and `lease_id` match the controller's `continuation_binding`
and the continuation observation. The observation must positively confirm the
lease and give an expiry strictly later than evaluation time. Missing, expired,
unconfirmed or conflicting bindings reject. The controller must establish unique
session/lease identity through its real lease service; these strings do not
acquire a lease. A stopped session needs separately reconciled restart/transfer
authority, not an implicit continuation. Lifecycle evidence is exclusive:
new uses neither continuation nor transfer, continuation forbids transfer, and
transfer forbids any continuation evidence, even an otherwise matching record.
Transfer also requires the observed replacement owner to acknowledge the exact
request hash. Missing acknowledgement, a different replacement owner, or an
acknowledgement for an older/different request rejects. The trusted collector
must verify this acknowledgement; a supplied boolean is not proof of delivery.

Unknown effects reject; already-completed effects require reconciliation without
reapplying them. Idempotency keys bind retries, but this function owns no durable
effect ledger and cannot provide exactly-once execution. An identical request,
observation, pins and evaluation time returns an identical receipt without
mutating any inputs. Offline evaluation returns `parked`/`park_only`, preserves
other rejection reasons and never permits task effects.

## Precise integration boundary

The controller must supply authentic, current authority pins from its existing
claim/approval registry; a worker must not generate its own trusted pins. A
separate trusted collector must actually verify host/OS, Git head/branch,
worktree and purpose manifest, scope inventory, readable input bytes/schema and
freshness, resources, prerequisites, writers and prior effects. Schema validity
and caller booleans do not establish truth; every receipt explicitly carries
`evidence_truth_verified: false` and `execution_authorized: false`.

An executor must bind the receipt hashes to these exact inputs, atomically acquire
an exclusive writer lease, recheck head/input/ownership/approval state immediately
before effects, enforce concrete allowed paths/effects, and record effect and
recovery outcomes durably. Those operations, independent review, hosted focused
tests and real admission acceptance are remaining gates for existing owners.
This increment adds no launcher integration, live data collection or activation.

Only JSON-compatible values are accepted; non-JSON values/nonfinite numbers and
invalid evaluation timestamps raise an error before any action. Structurally
invalid contracts produce rejection receipts. Date-time checks are explicit
RFC3339 with timezone and do not depend on optional jsonschema format packages.

## Evidence and tests

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -m unittest discover -s orchestration/execution_admission -p 'test_*.py' -v
```

Synthetic positive cases are labelled fixtures, not real executor proof.
`observed_fixtures.json` retains redacted workstation launch and data-continuation
shapes projected into **negative** cases; host and private branch/head fields
are fixture aliases, not executor proof; other contract values
in those tests are synthetic. Private paths and provider data are absent. Neither
fixture claims writer cessation or live admission. #207 files were not changed.
`validation.json` retains actual local attempts, including the initial failing
timestamp case and its successful correction. The repaired revision still needs
independent rerun; no hosted runner has executed this increment.

Independent review of initial head `ce013f62d6f8b33c8f81f23067410e393e3cede5`
reported two eligibility defects despite passing the original suites. Both were
reproduced locally with failing regression tests before the session/lease and
lifecycle repairs above. See the appended attempts in `validation.json`.

## Integration with Dot's top-level plan

This is the admission component of Dot/B00's existing system plan, not another
controller or task queue. Canonical queue: [#136](https://github.com/whiterosecoffee/_BASKET/issues/136).
The parent controller thread owns plan reconciliation; this folder owns only the
bounded validator. `task.json.integration` records the canonical queue,
reviewed implementation revision and unresolved integration gates.

Dot's room record at 2026-11-12T21:35:42.428363+00:00 reports an independent recheck
of the repaired local validator: 46 admission tests, 10 protocol tests and the
original negative probes passed. This is a retrieved controller report, not a
new independent run by this worker. The implementation revision is
`3395a0a41371c80282114b748f44e5673cb1a322`. Publication and session-launch
enforcement were outstanding at that report. Portable baseline `52466d0` was
subsequently published; session-launch enforcement remains outstanding. Local
qualification is not system integration.

| Existing system-plan step | This component's contribution | Remaining owner action |
| --- | --- | --- |
| 1. Common launch contract | Request schema, scoped manifest and purpose README | B00/template owner reconciles adoption with #134/#201; no global policy edits here |
| 2. Admission gate | Locally qualified pure validation and session/lease checks | Existing controller/executor owner supplies real observations and enforces leases before effects |
| 3. Source-to-consumer contract | Reject missing, stale or incompatible declared inputs | Existing _FETCH provides qualified local data/manifests; _MAP resolves location/freshness; analysts consume them |
| 4. Recurring jobs | Idempotency and uncertainty checks only | Existing scheduler/runtime owner proves locking, restart and catch-up; no scheduler acceptance claimed |
| 5. Result contract | Hash-bound receipt and preserved test/failure evidence | Controller distinguishes launched, executed, tested, independently accepted, integrated and operational |
| 6. Tested reuse | Synthetic cases and negative real-observation projections | Qualify the existing data worker and one code worker through the actual launch path before wider adoption |

Preserve the user's top-level `_TICKERS` direction: `_BASKET` is a collection of
tickers, and raw data stays private/untracked. This validator does not choose a
storage root, move data, duplicate maintained datasets or modify analyst files.
Actual location, source-manifest and coverage evidence must come from the current
_FETCH/_MAP owners. The older #207 fixture remains historical identity evidence;
it is not a claim to own or replace the current data maintainer.

Next controller action: bind this exact locally qualified implementation to the
existing launch-path owner for a bounded observation/lease integration, preserving
the separate denied-publication gate. Require a real blocked-launch/no-effects
case, a valid code-worker case and a valid data-worker continuation before marking
the admission step enforced. Worker capacity, current data readiness and successful
handoff delivery remain unverified here. The final worker return carries this
reconciliation to the parent; no global queue, public issue or other owner's file
was updated by this documentation change.

## Portable publication boundary

Only this eight-file subtree is carried into the publication branch. Internal
conversation identifiers and private host/data-worker identities are omitted or
replaced with fixture aliases. Prior local commit hashes identify historical
review evidence and need not be reachable from this portable branch. No raw data,
credentials, absolute workstation paths or conversation excerpts are included.
The current portable bytes require their own test run; historical independent
review is not automatically independent acceptance of this new commit.

## Handoff methodology disposition

Inspected the [five proposed gaps at pinned source de49f7b](https://github.com/whiterosecoffee/_BASKET/blob/de49f7b71334830648d94a211696a2d9cb2325ff/orchestration/handoff_loop/methodology-gaps.json)
once. Its requirements and acceptance cases are owner-handoff proposals, not
authority to modify launchers, schedulers, shared protocol or another owner's
files. The machine-readable disposition is in `task.json.methodology_handoff`.

| Gap | Admission disposition | Remaining acceptance |
| --- | --- | --- |
| Actual host / environment | Host and OS pins and offline parking already evaluated; no actual host collection or launch binding | Existing executor owner binds environment identity and observes wrong-host/offline launches denied before execution |
| Atomic ownership / worktree / dependency routing | Scope containment, observed isolation, inventory completeness, prerequisite confirmation and continuation lease checks exist | Launcher must atomically prevent concurrent writers and preserve dirty work/ancestry; controller routes out-of-scope dependencies to existing owners |
| Publication privacy | Portable baseline excluded internal routing/private identifiers and was tested and published; scoped diff scan repeated for this increment | Exact publication history/diff scanning remains a publishing-owner obligation, not a property this pure evaluator proves |
| Durable resume / schedule / transfer | Added replacement-owner acknowledgement bound to exact request; old-writer retirement, active-writer rejection and uncertain-effect checks retained | Checkpoint reread, persistent schedule target, duplicate-wake coalescing and stale-writer fencing require existing controller/scheduler integration |
| Trusted observation adapter | Collector/request pins and timestamp rejection exist; receipts explicitly deny evidence-truth verification | Independent adapter must establish authentic host, owner, activity and criterion-bound receipts; forged evidence and session-start-only acceptance must fail a real integration probe |

The new acknowledgement contract tightens the draft-v1 transfer
observation shape: callers must supply `replacement_owner`,
`replacement_acknowledged` and `acknowledged_request_sha256`. This is structural
and consistency validation, not a signed acknowledgement service. No caller
integration is claimed. Remaining handoffs stay with existing owners; no new
worker, scheduler, runtime registry or canonical-schema change is introduced.

Next: the controller routes the pinned candidate to the existing observation and
launch-path owner for a bounded real integration probe, retaining separate
checkpoint/scheduler and publication-approval gates. This disposition is not
acceptance of any of the five end-to-end methodology cases.
