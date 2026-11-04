# Source/gate evidence binding audit — B00-63

Owner: B00, parent B00 orchestrator. Issue #63; branch `work/63-source-gate-audit`.
Exclusive writes: this directory only. Read-only dependencies: #36 audit, B13 #31,
B01 #46, current worker protocol and existing task/resolution schemas.
No writes to planner, CI, shared schemas, financial models, ticker records, or
retirement intake. This helper does not replace worker_protocol.py, collect GitHub
state, schedule work, or approve a merge.

## Purpose and boundaries
Detect the specific two-revision failure exposed by this conversation: green CI
at a gate commit may execute an older, separately pinned source. Existing worker
protocol checks remain authoritative for task/PR ownership and readiness.
This helper accepts a caller-verified narrow projection, checks both source and
gate revisions, and returns review evidence only. It cannot authenticate caller
assertions, inspect workflow contents or logs, establish coverage, or verify main.
Never use its output alone to label a worker component_verified.

## Runbook
From repository root:
```sh
python -m unittest discover -s orchestration/audits/source_gate -p 'test_*.py' -v
python orchestration/audits/source_gate/check.py orchestration/audits/source_gate/historical-component.json
```
Exit 0: revisions match and run succeeded. Exit 1: evidence mismatch or non-success.
Exit 2: malformed/unavailable input. Missing evidence fails closed. No network,
provider entitlement, credentials, persistence process or automatic retries required.

## Inputs, outputs and restart
Input is exactly the seven fields used in historical-component.json. The four SHAs
must be full immutable Git revisions; source_binding is immutable_dependency or
reviewed_checkout. The caller must verify source head, gate head, run SHA,
conclusion, run URL and actual executed-source proof from GitHub checkout/logs.
A workflow pin by itself is not execution proof.
Output: component_evidence_matches, reviewed_source_exercised, blockers,
dependency_fingerprint, integration_verified (always false).
These are local helper fields, not a new shared schema or lifecycle vocabulary.
Canonical sorted JSON SHA-256 is the idempotency/checkpoint key. Same record gives
same result; changed source/gate/run/binding produces a new fingerprint. The helper
has no mutable checkpoint store; resume with the saved caller evidence.
Never overwrite a historical evidence record to make it reflect a current head.
On transient acquisition failure the collector, not this helper, decides retries.
Invalid input requires corrected evidence, not blind retry.

## Method and freshness
Discover relevant source/gate → acquire actual GitHub proof → normalize seven fields
→ check revisions/conclusion → persist evidence through existing worker reporting
→ independently validate → refresh when relevant source or gate changes.
Do not invalidate just because an unrelated worker ran. Refresh evidence before
each operational review; this offline helper does not determine evidence age.

historical-component.json preserves the component observation previously verified
in this thread on October 18, 2026, tied to run 39094901748 and issue #35 comment
6245350969. Exact retrieval time is unknown and deliberately not fabricated.
It is a historical regression fixture, NOT a live claim about current PR #31,
integration, valuation or SFTBY NAV. Current PR #31 has advanced since that proof.

## Lifecycle and obligations
Use existing vocabulary: available is an unclaimed proposal; claimed maps to
claimed; implementing to building; testing remains building with checks recorded;
review-ready to review (component_verified only after mandatory independent
criteria); integration-blocked to integration_blocked; integrated requires merged
source and independently verified main; retired is conversation disposition,
not a new implementation state. Keep issue open until B00's accepted disposition.
Use basket.worker_task@1 and basket.worker_resolution@1 in #63; do not create a
parallel worker status registry. PR #107 separately owns general worker-v2
documentation; this runbook describes only this helper.

## Failure register and acceptance
- Stale source pin: run success cannot certify a new source; rejected and tested.
- Stale gate SHA: rejected and tested.
- Skipped/pending/failed/cancelled run: never success; rejected and tested.
- False reviewed-checkout declaration: executed source must equal run revision.
- Malformed evidence: exact fields, immutable SHA and repository run URL required.
- Local pass inflated to integrated: integration_verified is always false.
- Lost October scratch checkpoint: source recreated from the visible conversation;
  no claim that uncommitted scratch was durably available.
Ten local tests include CLI exits, deterministic replay, no input mutation,
historical fixture, missing evidence and revised inputs. Dedicated CI integration
and independent B01 assessment are not implemented by this worker.

## Remaining owners
B01: if this helper is adopted, independently run the command above on its exact
PR head; adding it to shared CI is a separate B01 decision. B00: review integration
and existing #36 queue registration. B00 #29 / B04 #30 / B09 #28 retain contracts,
valuation and NAV; none blocks delivering this review helper. No new finance work.
Priority: review this bounded PR; adopt only if useful beside worker_protocol.py.
Workflow parsing, automatic collection and project-wide readiness are optional,
not unfinished obligations.
