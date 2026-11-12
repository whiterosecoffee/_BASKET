# Offline run-receipt qualification

Issue #246; B00 exclusive scope `orchestration/qualification/run_receipts/**`.
This is a **qualification specimen for the November 12 receipt convention**, not a
canonical runtime schema, scheduler, controller, queue, lock or execution engine.
It supports evidence review by #234/#236 without changing their records.

## Run

Requires Python 3.10+ and `jsonschema>=4.23,<5` (tested with Python 3.12.14 and
jsonschema 4.26.0). Once that ordinary dependency is available, execution is fully
offline. No optional format package, archive, laptop, repository import, provider,
API, credentials or network lookup is required. Provision dependencies separately
if absent; the validator never downloads them.

From repository root:

```sh
python -B orchestration/qualification/run_receipts/validate.py orchestration/qualification/run_receipts/specimen.json
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s orchestration/qualification/run_receipts -p 'test_*.py' -v
```

Or copy this directory elsewhere and run `python -B validate.py specimen.json`.
CLI input is one JSON receipt or an array; stdout is deterministic JSON; exit 0
means structurally valid, exit 1 means invalid/input error. `validate(receipts)`
is the in-memory API and does not mutate its argument. No output files are written.
CLI reports the input byte SHA-256. Errors are deterministic for identical input.
Use `read_json` for strict JSON parsing (duplicate keys and NaN/Infinity reject).

## Meaning and limits

Every receipt names `run_id`, `checked_at`, `subject_revision`, checked `sources`
with revisions and/or watermarks, `new_deltas`, `outcome_state`, `owner`,
`acceptance_evidence`, `next_action`, `blocker` and `recheck_condition`.
It also lists `evidence` and `test_evidence`. `subject_revision` may be null only
for `monitoring_only`: a non-Git monitoring run must not invent a commit SHA. All fields are mandatory; arrays may
be empty where there is no evidence. `blocker` is null when absent, except for `blocked` and `awaiting_approval`. Source revisions
are exact Git SHA-1 strings, following existing repository evidence conventions;
other source identities use a nonblank opaque watermark. No source may lack both.
Timestamps require timezone-bearing RFC3339 form and valid Python datetime values
(leap seconds are outside this specimen's profile). A source check cannot occur
after the receipt check. This does not prove freshness against the current clock.

| State | Meaning in this specimen |
| --- | --- |
| `monitoring_only` | Checked named source identities; no new delta and no advancement claimed. |
| `ready` | Owner asserts readiness; validation does not dispatch work. |
| `working` | Work claimed in progress; completion is not implied. |
| `awaiting_evidence` | Evidence needed before a stronger outcome claim. |
| `awaiting_approval` | Requires blocker reason, pending action, named `approval_authority` and explicit unblock condition; the receipt grants no authorization. |
| `blocked` | Reason, corrective action and unblock condition are all explicit. |
| `tested` | References at least one passing executed test record with command, positive count, zero errors/failures/skips and matching revision. |
| `accepted` | References at least one passing acceptance record with criterion, reviewer, artifact and matching revision. It does not imply merge or integration. |

These are outcome labels, not a transition graph. `accepted` need not imply a
code test: a review-only outcome may have acceptance evidence without test evidence.
The scope/coverage of tests and the authority of the accepting reviewer require
external review. Every receipt carries one next action and a recheck condition.

| Evidence tier | Structural requirement | Still needs independent checking |
| --- | --- | --- |
| `local` | Artifact locator and execution/result metadata; passing tests and acceptance require exact revision. | Artifact exists, execution happened, result and source identity are true. |
| `published` | Artifact URI and full 40-character revision matching the receipt subject. | Published bytes actually match the claimed revision. |
| `CI-verified` | Published requirements plus passing executed CI test evidence. | Actual workflow/log identity, revision, counts, coverage and conclusion. |

Dispatch/schedule evidence is `not_executed`/`not_run`; it cannot satisfy test or
acceptance evidence. All non-null evidence revisions must equal `subject_revision`.
Test and acceptance IDs must resolve to passing records of the proper kind.
Evidence IDs and source IDs must be unique. Deltas must name checked sources.

A valid receipt always returns `claims_verified: false` and
`validation_scope: structural_only`. The synthetic CI fixture deliberately uses
`example.invalid`: passing validation cannot authenticate a real run or URL.
No URL is fetched and no command in a receipt is executed.

Duplicate run IDs are compared only within the supplied batch. Structurally
identical JSON objects (ignoring key order, preserving array order) are accepted;
conflicting content rejects. The caller must supply prior receipts for cross-batch
comparison. There is no durable deduplication ledger or concurrency protection.
Input byte identity and semantic duplicate identity are separate concepts.

## Existing contract mapping

`mapping.json` pins the inspected read-only authorities. #232/PR233 owns a
transactional checkpoint (`stage`, fence, attempt, expected target revision), with
an intentionally open `receipt` object. This specimen qualifies review evidence;
it does not copy that recovery schema, import it, emit its checkpoints, or map
outcome labels automatically to transaction stages. Their meanings differ.
Existing `schemas/worker-evidence.v1.json` and `worker-resolution.v1.json` remain
the canonical GitHub evidence and worker reporting authorities. Publication and CI
claims here adopt their exact-revision and execution distinctions. This specimen
never generates `component_verified`, `integrated` or a worker resolution.

## Evidence

`specimen.json` and every record in `cases.json` are synthetic. Sixteen actual local
unittest methods exercise 46 corpus cases and the two review findings plus required-field omission, strict
JSON parsing, CLI error exits, unchanged bytes, batch repeat and standalone-copy
checks. `validation-evidence.json` is the immutable initial execution/hash snapshot at
PR head `f1625fe`; its hashes describe that earlier tree. `review-evidence.json`
records the follow-up probes, corrected behavior and current tested file hashes. Shared CI discovery is unchanged and does **not** discover this directory;
a green shared workflow is not hosted execution of these focused tests. Independent
review, real operational receipts, durable restart behavior and canonical adoption
remain outside this bounded acceptance. No raw data or private conversations are
included.

## PR256 static-review disposition

At `f1625fe242f1ac3f90a652ced2320e4e9ce4c764`, a probe confirmed that
`awaiting_approval` with a null blocker passed. This was a resume-information gap.
The pre-adoption specimen now requires the blocker fields plus
`approval_authority`; missing or blank values reject. Structural validation cannot
determine whether the named authority has permission, the action description is
sufficiently precise, or approval has actually been granted.

Cross-loop sources with different revisions and separate receipts for different
subjects already passed. A single receipt still qualifies evidence about one
subject revision; foreign-revision evidence rejects deliberately. Supply a batch
with distinct run IDs for multiple subjects. Source watermarks can identify non-Git
inputs, but are not automatically immutable or authenticated.

The mandatory subject commit was unnecessary for a non-Git **monitoring-only** run.
That state now permits null `subject_revision` while preserving checked source
identities and zero deltas. This is not a general revision bypass: tested, accepted,
published and CI evidence still require the exact Git revision. A non-Git acceptance
artifact or single aggregate acceptance over several subjects remains unsupported.
If real receipts demonstrate that need, propose a separately reviewed typed
subject identity (for example immutable content digest plus source namespace) and
explicit per-evidence binding. Do not overload watermarks or relax equality now.

`test_review.py` executes positives and adversarial cases for both dispositions.
All review inputs are synthetic; passing output still says `claims_verified: false`.
