# Trigger admission boundary: blocked live, tested simulation

This increment does **not** establish real scheduled-trigger integration. It
implements a live entrypoint that fails closed, plus a separate simulated binding
contract composed with the accepted disposable dry-run machinery. No schedule,
permission, routing configuration, credential or original checkpoint is changed.

## Actual interface assessment

Read-only `automations.peek` found the existing Handoff automation enabled with
an hourly recurrence. Its prompt references the existing worker, but a prompt
reference is not an authenticated invocation binding. The specific-task lookup
returned `run_details.last_run: null`, `latest_result: null`,
`delivery_status: unknown`, `environment_selection: inherited`, and no explicit
environment records. Null history does not prove the task never ran. A configured
schedule or last-run timestamp cannot supply an original run ID, prove delivery,
establish current liveness or demonstrate exclusive ownership.

The current workstation/session identity was checked locally and matched the
existing worker. That observation is not an authoritative scheduler invocation or
lease-service attestation. The current work arrived as a forwarded delegation;
its text and identifiers do not establish scheduler authenticity. Raw automation
prompts, task/thread/session IDs and private host data are not published.
`trigger-boundary-evidence.json` records sanitized actual findings, separately from
simulated tests and unavailable interfaces.

## Live entrypoint

`admit_live_trigger(checkpoint_path, invocation=None)` always returns blocked with
the exact missing interfaces. It does not open a checkpoint, read a source,
initialize state, schedule anything or call the dry-run writer. Caller-supplied
`verified: true`, plausible IDs, copied task configuration or forwarded prompts
cannot enable it. This is deliberate: there is no installed authoritative provider
adapter in the current scope. Only a separately qualified provider implementation
may replace this unconditional boundary; no dynamic import or credential mechanism
is introduced to pretend otherwise.

Required missing interface, owned by the platform/controller and lease owner:

1. **Authenticated current invocation:** immutable provider/automation/original-run
   identity, distinct retry-delivery identity, scheduled/issued/observed timestamps,
   actual target session/environment and a verifiable binding to the current
   invocation. Obtain via a trusted platform callback or direct authoritative run
   lookup; define the trust root and verification method. A copied JSON envelope
   or self-issued signature is not sufficient. Retries preserve original run ID.
2. **Current ownership observation:** independently verified owner, current session,
   actual environment/host, branch/head, scope and observation freshness. Environment
   variables and self-asserted worker registries alone do not establish exclusivity.
3. **Exclusive lease observation:** authoritative lease ID, holder/session/owner,
   current fence, exact subject/checkpoint binding, observation time and expiry,
   plus revocation/recheck semantics. The existing admission owner must enforce
   fence and lease changes; this code does not acquire or renew a lease.
4. **Controller pins:** independently approved target and disposable checkpoint
   identity/head/implementation binding, distinct from producer assertions. Bind
   the event to those pins immediately before persistence and recheck lease under
   the same enforced ownership boundary. No live dispatch authority is implied.

Without those observations there is no supported real trigger to admit. Do not
change the existing automation's schedule/prompt merely to inject fabricated IDs.

## Explicit alternative: simulated binding

`simulate_binding(pins, trigger, owner, lease, now=...)` accepts **only**
`provider: fixture-scheduler` and `mode: simulated`. These versioned output shapes
are component-local drafts, not extensions to canonical worker schemas. It rejects
missing/extra fields, unsupported origin, stale/future/inconsistent times, mismatched
target/head/checkpoint, missing/inactive owner, non-boolean exclusivity, wrong
lease/fence and expired lease. Simulation pins are fixtures, not trusted authority.

The bounded wake key hashes provider, automation, original run ID, target session,
environment, checkpoint identity/binding and head. Retry delivery IDs are excluded
so repeated delivery of one original run generates the same durable key. Scheduled
time remains in the wake body, and changing it under the same key is rejected by
the existing dry-run writer. Original-run identity is hash-bound, not authenticated
by this algorithm. Expected checkpoint binding hashes its immutable schema,
disposable marker, harness identity, head and implementation hashes.

`deliver_simulated_trigger(...)` validates the fixture binding and checkpoint, then
calls the existing `deliver_supplied` with that deterministic wake. Existing
reread/CAS/lock/atomic-readback and durable replay protections remain in force.
It cannot call the live collector or a session dispatcher. The caller must retain
the external original event to resolve the opaque hash key; this is not a second
event queue or real ownership registry. Existing receipts do not bypass fresh
simulation owner/lease validation on a subsequent invocation.

Both APIs explicitly keep actual_trigger_verified, ownership_verified,
lease_verified and dispatch_authorized false. Successful simulation is not real
trigger admission. The only positive binding evidence in this increment is
simulated; actual evidence supports the missing-interface disposition.

## Tests and next permitted step

Run the prior five suites plus
`python -m unittest orchestration.handoff_loop.test_trigger_bridge -v`.
The new tests cover deterministic original-run binding, changed delivery IDs,
restart replay, mismatched session/checkpoint, missing/stale owner or lease,
incorrect fence, malformed evidence and unchanged bytes on denial. Live-boundary
tests prove it performs no checkpoint read/write, process/dispatch call or dry-run
delivery, including when handed a forged verification claim.

Next: Dot independently verifies this exact boundary and the recorded automation
lookup. Route one concrete interface request to the existing platform/controller
and lease owner: expose read-only authenticated original-run plus current target
owner/lease observations. Once available, qualify a single event-to-disposable
checkpoint binding. Any schedule change or operational routing requires a separate
bounded authorized step. The live boundary remains blocked in this publication.
