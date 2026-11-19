# Synthetic observation and receipt adapter

This is a bounded offline port, not a trusted real collector. Input contract:
`basket.handoff_synthetic_input@0.1-draft`; output contract:
`basket.handoff_synthetic_normalized@0.1-draft`. The existing objectives schema and
evaluator remain unchanged. All output carries `mode: synthetic`,
`evidence_truth_verified: false`, `execution_authorized: false`. A simulated continue
decision is never permission to dispatch. No filesystem/network/process operations,
credentials, CLI, new queue, leases or scheduler are introduced by this adapter.

## Existing contracts inspected and reused

| Source | Reuse and boundary |
| --- | --- |
| Handoff core at `a0e8f1bbde4585b2bb16e4639548b5f18bc6be6d` | Directly imports `digest`, `subject_digest`, `criterion_digest`, `validate` and `evaluate`. Does not duplicate acceptance/dependency/wake policy. |
| Execution admission at `baba85f89ed90116345754bc2e457354e1f2f26b` on `work/local-20261112-execution-admission-portable` | Inspected README and receipt schema. Reuses the separation of request, independent caller pins, observations and hash-bound output; eligible never means execution authorized. Its full launch schema is not an observation receipt and is not silently converted or copied. |
| Run-receipt qualification #246 / PR256 at `2f395d475abace7fe58afbb9f0c5fa3d596c25e2` | Inspected documented source/subject revision, source identity, test execution and acceptance evidence contracts. Uses exact revisions and separate test/review kinds. That specimen remains structural-only and is not a live collector or imported runtime dependency. |
| Existing worker bridge README and host receipt on base `74d913e8913d630d85451344689e093aeea07efc` | Execution/start acknowledgement is not objective acceptance; old observed host receipts are not current ownership evidence. |

No other owner's files were changed. Cross-scope integration is a finding, not an
allocation or completed handoff. Canonical worker evidence/resolution records and
GitHub remain authoritative; this synthetic envelope does not extend their schemas.

## API and input

`normalize(state, envelope, pins, now=..., max_age=300)` returns a detached packet.
`evaluate_synthetic(...)` additionally calls the existing evaluator for a simulated
decision. Both are deterministic for identical arguments and never mutate inputs.
`load_json(text)` is the optional strict decoder: duplicate keys and NaN/Infinity
reject. Python input rejects non-JSON values/nonfinite numbers. Unknown fields reject.

Pins are a separate caller argument containing exactly `subject_digest`, `revision`
and `sources`. The subject is the existing core's hash of claim and objectives.
Revision is an exact lowercase 40-character Git SHA. Sources are unique records
`{id, identity, revision}` with synthetic:// identities and exact source SHAs.
The envelope's source inventory must equal the separately supplied pins. In a real
adapter the caller must obtain these pins from authorized independent records;
self-asserting matching pins in a synthetic fixture proves no authority.

Envelope fields are exactly `schema`, `mode`, `wake_id`, `subject_digest`, `revision`,
`sources`, `observations`, `receipts`. Each observation has unique `id`, `source_id`,
`subject_digest`, `revision`, numeric UTC epoch `observed_at`, `field`, `availability`
and `value`. There must be exactly one record for each claim field (environment_id,
host, owner, session, branch, worktree, scope) and each boolean flag (online,
single_writer, active, approval_pending, handoff_requested, checkpoint_due).
Available identity values must match the pinned subject; flags must be actual bools.

Availability is `available`, `unknown` or `unavailable`. The latter two require null
values and return `status: incomplete`, `observation: null`, empty receipt map and a
blocked simulated decision. Their distinct labels and provenance are preserved;
neither is coerced to False. An available false online value represents an offline
observation and the evaluator parks it. Absent records are malformed, not inferred.

Receipt records share the identity/revision/time fields and add `kind`, `payload`:

- `test`: objective, command description, executed=true, result=pass, positive
  integer tests count, zero integer failures/errors/skipped. No command is executed.
- `acceptance`: objective, criterion, criterion_digest, result=pass, reviewer,
  artifact. The objective, criterion text hash, exact artifact revision and evidence
  reference must all bind to the supplied snapshot. A test/start receipt cannot
  satisfy acceptance.

Other kinds, including dimension, dispatch and session-start, reject. Receipt IDs
must be unique across the whole batch and referenced by the matching objective;
acceptance IDs must also appear in their criterion. The existing core validates
hierarchy, dependencies, gates and receipts after normalization. Passing synthetic
acceptance is a simulation of assertions, never real independent acceptance.

Freshness rejects missing, malformed, future or older-than-max_age timestamps for
every record. `verified_at` on the derived observation is the oldest timestamp
across observations AND receipts, so a newer host sample cannot refresh stale
review evidence. Output includes per-field provenance, receipt provenance, input
and pin digests, evaluation time and freshness bound. Re-normalize at each use;
there is no persistent freshness/authenticity guarantee in a cached packet.

Malformed inputs raise ValueError without partial packets or writes. Unsupported
handoff transfer receipts are not constructed: a handoff request can only reach
the core's checkpoint-required state without real retirement/acknowledgement data.

## Reproducible manual test

Run `python -m unittest orchestration.handoff_loop.test_core orchestration.handoff_loop.test_adversarial orchestration.handoff_loop.test_synthetic_adapter -v`.

For a bounded synthetic demonstration, import `fixture` from
`orchestration.handoff_loop.test_synthetic_adapter`, then call
`evaluate_synthetic(*fixture(), now=100)`. The fixture is generated from the safe
example, uses fabricated source/subject revisions and does not contain live data.
Tests cover repeat normalization, duplicate wakes through the existing temporary
atomic writer, rejected-input non-mutation and oldest-receipt expiry. These are
local synthetic tests, not live source or scheduler execution evidence.

## Next gates, separately owned

**Real read-only adapter:** choose one existing source and collector owner; verify
an independently obtained pin/allowlist, actual source identity and returned bytes,
exact Git/artifact revision, current ownership inventory and source timestamps.
Bind receipts to those verified bytes and authorized acceptance authority, without
letting producer assertions become trusted pins. Define unavailable versus absent
versus conflicting data and pin refresh/revocation. Reconcile this narrow port with
the admission owner and #246; test spoofed source, changed head, partial inventory,
stale/replayed evidence and real read-only denial. No persistent credentials or
broader permissions are provided by this increment.

**Live dispatch:** existing controller/executor owner must separately enforce an
atomic exclusive session/lease, immediate state/approval recheck, scope and effect
limits, durable idempotent effect receipts, exact persistent scheduler routing and
explicit recovery/transfer. Read-only source qualification alone cannot satisfy
these gates. No launch enforcement is implemented here.

Next bounded acceptance step: Dot reruns this adapter's positive fixture and named
adversarial cases at the published exact head, verifies all prior core tests still
pass, and decides whether to allocate a single real read-only source adapter.
