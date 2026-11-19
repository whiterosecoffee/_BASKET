# Receiver readback and risk-based sanitizer evidence

This local synthetic profile adds receiver and quality-control evidence to the
existing purpose-specific temporal request. It reuses canonical artifact references,
lifecycle identity/hash definitions, local strict shape helpers and temporal
qualification. It implements no sanitizer, file reader, adapter, storage writer,
shared status authority, dispatcher or runtime.

## Receiver boundary

`receiver.examples.json` supplies low-risk historical and high-risk current
examples. The receiver declaration binds the exact request hash, artifact content
hash (including generation/revision metadata), risk-policy hash, intended consumer
and applicable temporal purpose. Checks and receiver receipts also bind the complete
transformation/audit/preservation pipeline hash. Readback content must hash to the expected
artifact and the readback result must pass. Receiver evidence must be distinct
from producer artifact identity. Changed request, purpose, consumer, artifact or
policy invalidates the receipt rather than inheriting an older acknowledgment.

Dispatch and producer-result fields are informational. Neither satisfies receiver
acknowledgment. Even valid readback does not imply consumer acceptance: `pending`
and `rejected` remain unusable. All required quality gates must pass before the
receiver's accepted declaration is reflected as `consumer_acceptance=accepted`.
A valid receipt may acknowledge delivery while quality failures still block use.
Missing acknowledgment blocks use without pretending the data itself failed QC;
invalid readback or failed/unknown quality checks mark it for quarantine.

## Risk-based quality checks

The existing engineering method (`architecture/BLOCK_ENGINEERING_METHOD.md`)
requires review of applicable attributes, explicit UNKNOWN, consequence-aware
independence and mandatory gates that cannot be hidden by a composite score.
This profile uses existing pass/fail/unknown evidence concepts, pending/accepted/
rejected acceptance, and blocked/review task vocabulary; it does not extend the
canonical worker schemas.

| Required at every level | Additional low-risk minimum | Additional high-risk minimum |
|---|---|---|
| Integrity, provenance, privacy, plus existing temporal qualification | Semantic validity | Semantic validity, coverage, units, conflict resolution and independent review |

The caller retains the policy independently, including intended use, failure
consequence, privacy requirement, risk and additional domain-check IDs. These
are an illustrative minimum option set, not a comprehensive domain-risk model.
Owners may require more checks; declared high-risk minima cannot be omitted or
silently downgraded. Every required check binds the same request, artifact and
policy. Every supplied unknown is retained in `unknowns`, including optional checks and
auditor-only results. Missing/unknown mandatory checks block use; every supplied
failed check is retained in `failures` and blocks use. Passing many other checks cannot compensate.

User assertions cannot pass sanitizer gates. High-risk independent review requires
the independent-evidence origin and a distinct reference and digest from producer
and other check evidence. This consistency rule does not authenticate independence.
Privacy is pinned in expected policy; changing placement flags cannot waive it.
The existing temporal validator still rejects missing/unknown historical coverage,
wrong session/basis, stale current watermark, superseded generation and as-of leaks.
A file's presence, location, dispatch status or producer success proves none of
currentness, coverage or semantic validity.

## Provenance and maturity boundaries

Claims retain their supplied text, evidence and origin as `user_assertion`,
`producer_observation` or `independently_verified_evidence`, with corresponding
asserted/observed/verified status. They must equal caller-retained claim records;
relabeling or elevating a claim rejects. A valid user assertion is retained as an
assertion, not discarded or converted into a verified fact. Corrections belong in
the existing append-only intake/reconciliation process, followed by new expected
inputs; this evaluator cannot rewrite the retained source.

All outputs have `execution_authorized=false` and `evidence_authenticated=false`.
`valid`, `receiver_acknowledged`, `consumer_acceptance` and `consumer_usable` are
computed **local declaration-consistency results**, not proof of real readback or
operational qualification. The resulting state is `review`, never operational or
integrated. Fabricating both packets and expected inputs can still create a
consistent story; authentic receipt collection, identity, signatures, destination
privacy and domain check execution remain external owner responsibilities.

_FETCH's intended ongoing live acquisition, standardization, sanitization and
requester-authorized private local persistence remain product requirements.
Massive remains adapter metadata; consumer use is a later read-only step. Offline
synthetic testing here does not narrow that product scope or claim live execution.
Historical data does not expire from event age alone; explicit temporal options
remain unchanged. No private destination is created or public data posted.

## Reproduce and hand off

```powershell
python -B -m orchestration.clean_templates.receiver
python -B -m unittest discover -s orchestration/clean_templates/tests -p test_receiver.py -v
python -B -m unittest orchestration.tests.test_clean_template_seed -v
```

See `receiver.validation.json` for producer counts and source/log hashes. Existing
lifecycle, semantic and temporal suites remain part of shared discovery. Independent
review must rerun this exact increment and mutate receiver binding/readback,
assertion provenance, risk requirements and unknown/failure dispositions. Preserve
the distinction between internal consistency and authentic external evidence.

Owner handoff: #103 reconciles canonical receipt/policy contracts; #105 reviews
semantics independently; #134 adopts generated examples; #201 incorporates the
methodology; #230 registers existing owner references. Existing _FETCH/runtime and
consumer owners implement real sanitizer checks and authenticated receiver readback
through the parent controller. No owner is dispatched or integrated by this local
packet. Governing adoption remains 0/8; no publication retry, merge or deployment.


## Expanded QC contract: transform, audit and originals

The supplemental review at `97edd0656c74b483b720ce2c1fd0124c00b01815`
accepted the original bounded declaration gate but found the expanded contract
incomplete. Three regression tests reproduced those gaps before repair: missing
lineage was accepted, an opaque audit reference could replace actual versioned
record contents, and optional provider-adjustment uncertainty disappeared.

The required `pipeline` now carries:

- `raw_input`: exact supplied original UTF-8 text and its artifact hash. Whitespace
  changes the raw hash; parsing/re-serializing the original is not preservation.
  Binary source encodings require a canonical-owner extension, not an implicit
  conversion here. Normalized generation JSON retains its existing canonical hash.
- `normalized_output`: the exact artifact already qualified by the temporal gate.
- `transform`: a standardizer declaration binding request, policy, raw-input hash,
  normalized-output hash, schema version, sanitizer implementation revision, runner
  identity/version and configuration digest. Its explicit assessed scope binds
  purpose, coverage digest and normalized-output stage.
- `audit`: a separately identified independent-auditor declaration with the same
  lineage and assessed scope, pinned auditor runner version and explicit results.
  Its content hash is checked; the independent-review check must reference this
  included record. An opaque unresolvable reference cannot substitute for it.
  Audit results must exactly match the supplied check/result list. The auditor's
  actor and evidence identity must differ from the standardizer's.
- `preservation`: a hash-bound declaration naming originals, normalized artifact,
  equal before/after original hashes and distinct original/output destinations.
  Output must be separate or a sidecar; the original artifact reference cannot be
  reused as the normalized destination. URI aliasing and actual immutability still
  require storage-owner enforcement.

The independently retained policy pins schema/sanitizer/configuration and both
runner versions. Missing records/versions, mismatched input/output/scope, changed
originals, same declared destinations, role collapse or inconsistent audit results
fail closed. This validates a declared lineage tuple; it does not execute the
standardizer, prove that transformation semantics are correct, authenticate either
runner, resolve evidence references, or establish actual originals preservation.
Those remain separately executed and independently accepted owner responsibilities.

## Unknowns and conditional use

`use_status` distinguishes `blocked`, `conditional` and `qualified` within this
local declaration profile. There is no blanket `confirmed` fact. `qualified`
means only that the explicitly assessed scope has no reported unknown/failure;
it does not confirm all possible provider semantics. In particular, matching an
adjustment-basis label is not proof of provider adjustment verification.

Optional unknowns block by default. An independently retained, purpose/consumer-
bound policy may list a specific optional check in `allowed_unknowns`; the result
then remains `conditional`, retains every unknown, keeps `consumer_usable=false`
and `consumer_acceptance=pending`. It does not grant permission to use the data.
Mandatory and risk-required unknowns cannot be waived. Extra failed checks always
block and quarantine. Evidence present only in the auditor result list cannot be
silently dropped; mismatched lists reject while retaining known uncertainty.

Canonical handoff: #103 reconciles lineage/version/preservation definitions;
#105 independently requalifies this exact new source; existing _FETCH coordinates
standardizer and separately assigned auditor requests. Runtime/storage owners
prove actual immutable originals, private authorized destinations and runner
receipts. #134/#201/#230 adopt only reviewed references through their existing
owners. This local repair does not staff or dispatch those lanes. Adoption is 0/8,
execution_authorized and evidence_authenticated remain false, and live product
requirements remain separate from this offline evidence.
