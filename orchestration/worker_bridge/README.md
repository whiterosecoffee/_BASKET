# Issue-to-worker execution bridge — B00 #136

This is a finite execution adapter, **not another scheduler, task schema, queue,
lease database or hosting service**. It composes existing components and keeps
GitHub issue/branch/PR/CI evidence authoritative.

## Recovered sources

| Component | Exact source | What is reused |
|---|---|---|
| Main | `afc4ada7bc6d7294071b3610fa77e59b206b6312` | Worker schemas, profile library, scopes, evaluator, B01 workflow |
| #106 / PR #107 | `eb099d8e2bf37918eaf11a46341289ff09651d9e` | Worker-v2 lifecycle; run `40927765356` succeeded at this head |
| #32 / PR #33 | `59a8e0eae91f96d64a1589ebfef03c4a7383662c` | `evaluate`, `collisions`, `attempts`, lease/event validation, fingerprints, complete PR collector |
| #78 / PR #79 | `0eae03d6a2e0b98209761a365b9c891ff7b7c48b` | Existing `basket.agent_assignment@1` transport envelope |
| #103 / PR #104 | `3908ef1dc33c65ee19e87b54a6d63a191659b9fa` | Component I/O/provenance/error boundary proposal; no new schema |
| B08 #53 / PR #55 | `24d77045575926be5499355f9d26de499ed2b5ae` | Runtime ownership boundary; existing service is a read-only snapshot, not an agent supervisor |

Dependency source is not copied or modified. `controller-lock.json` pins its Git
commit and content hashes. A mounted read-only checkout is required until its
owning PR is reviewed/integrated. The original audited source `192a31bed3858fc0fb0c0254cd85cf6672e49511` had
60 passes and one misaddressed retry fixture (T-001 events, T-002 assertion).
User-authorized maintenance corrected that fixture on its owning PR #33 and added
a B00 discovery shim. The current pin has 61/61 local controller tests and 111/111
independent B01 PR-CI tests passing at exact head (run `41172651296`). Production
controller bytes are unchanged. Original failed logs remain historical evidence.

## Smallest missing implementation

The existing controller decides policy and validates events. #78 documents transport
but supplies no executable adapter. This bridge adds deterministic selection from
the **existing** worker library, issue-bound authorization checks, envelope rendering,
one explicit executor call, and publication guards. It projects one authorized issue
into a transient controller call argument; it never writes another planner queue.

Both `contract_engineer` and `qa_reviewer` are reused from the library. Profiles
grant no new spark paths. QA cannot request the write-capable CLI sandbox. Scope
checks compare declared issue claims and all open PR files. PR exemptions must
match repository, task branch, main base and exact checkout HEAD. Missing or
ambiguous claims, dependencies, leases, attempt IDs and sources fail closed.

The owner grants existing `basket.agentic_event@1` events on #136. The current
lease event ID is the fencing value. Only the latest authorized pending attempt
can execute. Expired/missing leases do not reassign ownership. No global worker
capacity is inferred from open PRs or invented in a capacity attestation.

## Actual execution and its limits

1. A real GitHub issue and unique main-based branch were created after collision checks.
2. An authenticated native Codex CLI attempt exited **1 before model execution**:
   its in-process app server could not write its runtime state. Its empty native
   event stream, stderr, command and failed result are preserved in
   `evidence/ATT-136-engineer-1/`. Login status alone was never treated as execution.
3. B00 explicitly authorized recovery via the supported **host Codex worker
   transport**. `collaboration.spawn_agent` executed the existing contract-engineer
   profile and produced `test_agent_profiles.py`; the returned file hash and ten
   actual passing tests were independently checked by the parent.
4. A separate read-only host QA profile executed the tests and found four real
   authorization/publication defects. B00 fixed them, added regressions, and the
   QA follow-up verified the fixes. Receipts preserve the reviewed fingerprints,
   so an old review is not represented as a review of later source.
5. B00 owns commit/PR publication. Children were forbidden to commit, push, allocate
   issues/branches, change credentials, delegate again, merge or release.

The successful transport is **operator-mediated host execution**. It is not a
successful native CLI run, installed remote auto-dispatch service, unattended
scheduler or deployed B08 supervisor. The host did not expose an independently
verifiable model version; this remains unknown. The original failed CLI attempt
predates some hardening, including policy/attempt fingerprint binding; its logs
are retained as historical failures, not proof that current guards were applied.

The adapter's shell sandbox is a process boundary, not a per-file OS ACL. The
outer host must enforce the narrower instruction, re-read GitHub ownership and
compare all changed paths before publication. CLI log paths reject symlink
ancestors. Postflight rechecks source pins, lease/attempt identity, PR association,
checkout HEAD and stable source fingerprints. It rejects changes instead of
reusing a stale pass. There is no automatic retry after model failure/timeout.

## Interfaces and commands

Use the existing Python/jsonschema environment; no new dependency is introduced.
The CLI takes an owner-issued comment containing one JSON array of existing
controller events. The provider reuses #32's full PR collector and pagination.

```sh
python -m orchestration.worker_bridge.cli \
  --controller-root /path/to/pinned-controller-checkout \
  --lease-comment-id <current-owner-event-comment> --lease-id <current-event-id> \
  --profile contract_engineer --capability contract_governance --capability implementation \
  --attempt-id <authorized-pending-attempt> \
  --instruction orchestration/worker_bridge/implementation-instruction.txt
```

Without `--execute`, this renders a validated packet only. A configured authenticated
host may consume it through #78's operator handoff; packet generation alone is
never execution evidence. `--execute` requests exactly one native CLI invocation;
`--write` additionally requires an implementation-capable profile. `--own-pr` is
required once this task has an observed PR, and cannot exempt unrelated work.
Keep the dependency checkout at its pinned commit. The recorded lease is historical
and expires; it is not perpetual permission to replay these commands.

`COMMANDS.md` and `evidence/` preserve actual calls, outputs and source hashes.
No test double, injected collision or clock movement is called a real executor.

## Verification and acceptance

`orchestration/tests/test_worker_bridge.py` is a disjoint B00-owned discovery shim.
The existing B01 workflow already runs it; no CI-owned file is changed. It fails
if no bridge tests are found. Tests are offline, require no model calls/network,
and explicitly label controller doubles as doubles. Real pinned-controller
scenarios are separately recorded, not substituted for independent CI.

```sh
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s orchestration/tests -p 'test_*.py' -v
```

The local main-based suite has 82 passing tests, including 25 bridge tests. Eight
additional injected collision/fencing/expiry/source-drift scenarios passed against
the actual pinned controller. Their recovery consists of removing only the test
fixture or explicitly acknowledging a replacement test lease, not stealing a live
worker's scope or pretending a real host restarted.

B00 must fetch the exact PR head/files and independent B01 CI before acceptance,
then use the existing worker-resolution evaluator. Shared green branch validation
does not establish merged integration, persistent operation or a release. All
mandatory gaps stay visible in the issue's final resolution.

## Handoffs and blockers

- #32 / #65: fixture repair and independent exact-head controller verification
  are complete on PR #33. Its source is still unmerged and must be integrated
  through approved ownership/review, not vendored here.
- B08 #34/#53: provide a reviewed authenticated execution supervisor and writable
  runtime state if unattended/native execution is desired. Current snapshot service
  is read-only; this bridge does not add a competing runtime.
- B01: existing orchestration discovery runs unit guards automatically. Separately
  verify real controller and external transport before claiming hosted operation.
- No merge, release, paid external invocation, market-data runtime modification,
  ownership takeover or automatic worker launch is authorized by this component.

Priority verification update: `evidence/controller-repair-59a8e0e/` records the
current source pin, unchanged production hashes, local commands, and exact-head CI.
New negative scenarios explicitly replay a historical snapshot for testing only;
they do not renew the released live execution lease.
