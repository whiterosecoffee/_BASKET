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

## Full-conversation intelligence and closeout (protocol v2)

Coverage: the entire visible conversation and its tool results, including the
initial PR31 boundary audit, subsequent retirement requests, changing B13/B01
heads, user-authorized worker expansion, interrupted scratch implementation and
resumed closeout. Other conversations are not available in full; summaries and
receiver claims are not substitutes for their execution evidence.
Applied draft prompt: orchestration/conversation_closeout/HANDOFF_PROMPT.md on
work/169-conversation-closeout-cli, blob f3e6c4b8a656b27feeed4ea32b86792faa1a7be2.
It was not available on main at this review. This is a human review applying the
complete protocol, not a claim its optional CLI read or understood this transcript.

### Obligation ledger
- Initial source/contract-boundary audit: delivered, evidence and handoffs in #36.
- Preserve audit as executable worker: implemented in #63 / PR167; this directory.
- Domain tests: 10 local passes; exact committed source was fetched and matched.
- Existing task/resolution schema validation: prior ModuleNotFoundError corrected
  by installing jsonschema==4.23.0 in temporary /tmp/source-gate-jsonschema; both
  original payloads now pass Draft202012Validator with FormatChecker.
- Shared CI at code head 232c5dc19f3c7c9374587886f3624e8a2ed7e22f:
  run 41765677148 success. It does not prove this dedicated suite ran.
- Independent B01 check/B00 accepted disposition: requested, no receipt/execution
  evidenced in #63 at current review. PR unmerged. Do not call integrated.
- Queue registration #36, private contract #29, company valuation #30 and SFTBY
  NAV #28: externally owned; not requirements to implement this helper.
- Broader orchestration refactoring/automatic workflow parsing: deferred optional
  proposals. No additional framework, task queue or scheduler authorized here.

### Knowledge units and maturation map

**K1 — Bind evidence to both the program and the source it executes.**
Trigger: shared CI at B13's original commit was incorrectly easy to interpret as
proof of its unexecuted research checker; subsequent B01 CI used a separate source
checkout. Principle: an outcome certifies only the inputs actually exercised.
Mechanism: compare current source_head with executed_source AND gate_head with
run_head; require success; distinguish immutable_dependency from reviewed_checkout.
Method: collect heads and actual checkout/log proof, normalize, assess, fingerprint,
refresh after a relevant revision. Application: original B13 4528713e, expanded
fb87ad2d, repaired 316dbea5 and B01 8b2f7404 are different evidence vintages.
Families: PROV/REPRO/DBC provide revision lineage and exact input checks; analogous
to build attestations, not a claim of cryptographically authenticated provenance.
Destination: implemented check.py/test_check.py; extend existing worker_protocol
only after B00/B01 review, do not create a second canonical readiness evaluator.
Falsifier/limit: a caller can lie about executed_source; matching strings do not
authenticate logs, coverage or source truth. A manually declared reviewed_checkout
is not proof. Reconsider implementation if an existing attestation adapter supplies
this binding directly; reuse its proof instead of another parser.

**K2 — Keep independent readiness dimensions and local scope separate.**
Trigger: earlier replies declared retirement while required implementation had
only a claimed issue and lost scratch files. Principle: knowledge saved, local
execution, independent validation, accepted transfer and main integration are
different assertions. Mechanism: existing task/resolution checks and acceptance
IDs carry evidence; main verification remains external. Method: explicit
deliverable/owner/missing-criterion ledger, complete local work, then transfer.
Application: #63 cannot be called integrated merely because 10 tests pass.
Families: FSM/DBC/CQRS: commanded work differs from observed outcome; no new
lifecycle names or status registry. Destination: this runbook and #63 resolution;
general policy already belongs to WORKER_PROTOCOL.md and PR107. Consolidated,
not competing worker-v2 documentation. Optional adoption is not mandatory project
stabilization, and unrelated valuation backlog does not block a local closeout.

**K3 — Treat financial category and vintage equivalence as testable gates.**
Trigger: private-company financing, derivative commentary and gross stake
arithmetic could be promoted into issuer fair value or SFTBY NAV.
Principle: arithmetic correctness cannot establish economic comparability.
Mechanism: retain security class, value type, effective/available/ingested date,
gross/net entitlement and fund embedded base mark; reject unsupported conversions.
Application: 730+122=852 is one financing family, not independent marks; committed
cash is not funded cash; reported annualized revenue is not recognized FY revenue;
13% gross stake is not net parent NAV; replace embedded OpenAI in SVF2 while
preserving remaining holdings; bridge June/March/October vintages explicitly.
Families: PIT/PROV/DBC/FALS: availability guards against lookahead; typed claims
prevent false equivalence; falsifiers preserve uncertainty. These are methodological
family analogies, not externally researched historical citations.
Destination: existing B00 #29 fixtures, B04 #30 model and B09 #28 behavioral tests.
Transferred through #36; this evidence helper deliberately calculates no NAV.
Counterexample: all the 852*0.13 and -4% arithmetic can pass while NAV is unavailable.

**K4 — Dependency graphs should gate outputs without freezing research.**
Trigger: receiver issue dependencies could create a B04↔B09 circular wait.
Principle: distinguish information needed to prepare work from information needed
to publish a verified output. Mechanism: B00 accepted contracts precede consumer
integration; B04 scenarios feed B09; B09 can source baseline/create blocked adapter
earlier; B21 can retain hypotheses before eligible B02 causal evidence exists.
Method: attach a specific input/output acceptance to each dependency, use fixtures
while data is absent, and invalidate only when relevant source fingerprints change.
Families: DAG/HEX/MOD/IDEM: ports isolate producer and consumer; deterministic
fingerprints suppress unnecessary recomputation, not economic source acquisition.
Destination: existing #29/#30/#28/#36 and existing T-011/T-006 subject to current
queue-owner reconciliation. Do not create duplicate workers or modify its queue.
Limit: fixture correctness does not prove production input completeness.

**K5 — Persist checkpoints and reconcile actual files, not stale descriptions.**
Trigger: PR25 expanded from a single-file description; scratch code vanished
before persistence. Principle: review actual changed paths and durable outputs.
Mechanism: scoped branch, exact fetched content, failure→fix→retest records, explicit
requested/accepted handoff distinctions; never infer live capacity from drafts.
Method: inspect relevant PR paths, checkpoint code/test evidence promptly, leave
one next action. Families: EVS/POST/OBS/INFO: preserve failure lineage and compress
redundant status reports into one durable resolution without erasing history.
Application: independent B01 exposed eligible-stage KeyError, B13 repaired it and
B01 retested; this worker lost uncommitted scratch and recreated it.
Destination: #63 resolution and this runbook; #36's prior comments remain history.
Rejected alternatives: repeated prompt-only handoffs, parallel queue/scheduler,
and invented JSON Schema validator. Use installed jsonschema for canonical schemas.

### Observable execution-quality retrospective
Judgment aid for the whole visible conversation, not a completion percentage,
productivity metric or financial prediction. Each dimension 0–5:
objective control 3; execution conversion 2; reuse 4; ownership 5; verification 4;
dependency handling 4; resource efficiency 2; knowledge extraction 4; handoff
quality 3; closure discipline 2. Total 33/50 = 66/100. Later recovery does not erase
earlier incomplete execution. No token/time saving is claimed.

Three corrections:
1. Actual: repeated retirement prompts while helper remained scratch-only.
   Feasible alternative: inspect obligation ledger before declaring retirement.
   Root: transfer documentation substituted for executable acceptance.
   Prevention: #63/B00 review requires commit+PR+test evidence before disposition.
2. Actual: missing jsonschema treated as external blocker without installation.
   Feasible alternative: normal isolated dependency installation, now successful.
   Root: missing package conflated with unavailable credential/permission.
   Prevention: try one standard authorized installation; schema test must run or
   record actual installation denial, not just an import failure.
3. Actual: multiple overlapping #36 status comments and broad repeated PR reads.
   Feasible alternative: preserve immutable history but maintain one current
   resolution plus only material new facts. Root: no explicit handoff version/end
   criterion. Prevention: B00 compares source/gate fingerprints and acceptance IDs;
   receiver can identify exactly what changed and what remains.

### Ranked maturation disposition
Correctness first: B01 independently exercise exact-head source binding and B00
accept/reject helper beside worker_protocol.py (small estimated review effort).
Already incorporated: black-box revision checks, negative tests, fingerprints,
historical fixture and honest limitations. Consolidated: methodology, failure
register, state mapping and this conversation's lessons in this existing README.
Transfer: actual integrated-source CI proof and behavioral financial gates to
their existing owners. Deferred: automated workflow parsing/remote collection
until there is a demonstrated consumer need. Discard: another scheduler, central
status store, arbitrary prediction score, and source-truth claims from green tests.
No quantitative candidate ranking is needed for this small bounded review.

### Complete receiver prompt
Receiver B00, with B01 independent validation: continue existing issue #63 / draft
PR167 on work/63-source-gate-audit. Refresh its head and #63 comments first; do not
reuse stale code SHA as evidence for later edits. Exclusive scope of this worker is
orchestration/audits/source_gate/**. No planner/queue, shared schemas, CI, ticker,
valuation, NAV or other worker files may be changed by this audit worker.

Mission: independently validate/adjudicate this narrowly scoped revision-binding
helper, and record B00 accepted disposition in #63. Do not regenerate B13 research.
Reuse existing WORKER_PROTOCOL.md and canonical worker schemas. Do not start a new
workstream. Source code checkpoint 232c5dc19f3c7c9374587886f3624e8a2ed7e22f had 10
local tests, all committed files matching local text, and shared run 41765677148
success. Later README-only commits need their own current-head review. Original
task and resolution payloads on #63 now pass existing JSON Schemas locally after
isolated jsonschema installation; no independent acceptance or merge is claimed.

Preserve K1–K5 above: two-revision attestations, separate readiness dimensions,
typed/time-aware financial evidence, producer→consumer DAG and durable checkpoints.
The helper's seven-field input is caller-authenticated evidence, not a GitHub
adapter. Its output contains matches/blockers/fingerprint and always sets
integration_verified=false. Same inputs replay identically. New source/gate inputs
must invalidate old proof. False caller inputs remain an explicit trust boundary.
Use case: green workflow at one SHA can test a separately pinned old B13 SHA.
Counterexample: arithmetic pass or labels do not prove reconciled SFTBY NAV.

First execute at CURRENT PR head:
python -m unittest discover -s orchestration/audits/source_gate -p 'test_*.py' -v
python orchestration/audits/source_gate/check.py orchestration/audits/source_gate/historical-component.json
Expect 10 tests and historical component evidence only, never integration. Validate
#63 task/resolution payloads using Draft202012Validator + FormatChecker and current
schemas/worker-task.v1.json and schemas/worker-resolution.v1.json. Review CLI exit
0/1/2, stale source/gate, non-success, missing/invalid provenance, false checkout,
deterministic fingerprint and no mutation. Authenticate fixture ancestry as
historical only. Check actual shared workflow steps before claiming suite CI.
B01 owns any optional CI wiring; do not expand this worker to edit workflows.

Then B00 records accepted/rejected/deferred adoption with rationale. If adopted,
verify integrated-source execution and main CI only after authorized integration.
No merge/release authorization is granted. General worker-v2 documentation is
already in PR107; prefer consolidation over duplicate policy. #36 queue and
#29/#30/#28 financial work remain outside this local completion gate. Do not claim
B01 acted merely because the request was posted. Retire this chat after accepted
transfer/disposition is recorded, or explicitly accepted user transfer endpoint.
