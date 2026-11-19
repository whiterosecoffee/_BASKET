# Disposable scheduled-continuation dry run

`dry_run.py` is a deterministic delivery harness, not a scheduler installation or
live continuation runtime. It consumes a manually supplied simulated wake, an
existing read-only GitHub observation and a **new disposable** checkpoint. It
never accesses the original private objectives checkpoint, migrates state, calls
an agent/session API, starts a worker, changes permissions or mutates GitHub.

Three dimensions remain separate:

| Dimension | What this increment establishes |
| --- | --- |
| Schedule delivery | Manually simulated input; no timer or automation installed |
| Source retrieval | `deliver_readonly` uses the existing collector's two actual GETs; `deliver_supplied` uses fixtures/supplied responses |
| Scheduled execution | Always false; no dispatch authority or operational continuation |

GitHub metadata cannot establish local host/ownership/lease/approval facts. The
harness therefore does **not** forge those flags or call the evaluator as if they
were known. It produces a dry-run review disposition: review-next-step when all
observed exact-head CI runs passed, wait-ci when running, review-failure on failed
CI, request-evidence when unknown/incomplete, or park when the PR is closed. These
labels do not mean component tests ran, reviewer acceptance, or permission to work.
Unchanged source metadata on a distinct eligible wake records no-source-change.

## State and API

`initialize(path, harness_id=..., head=...)` exclusively creates
`basket.handoff_dry_run_checkpoint@0.1-draft` with `disposable: true`, pinned source
head and implementation file hashes, revision zero and an empty receipt list.
An existing file is never overwritten. Changed harness/collector file bytes reject
resume; create another disposable checkpoint after review instead of migrating.
Hashes identify the two component files, not a signed package or full dependency
environment. Local files, Python/runtime dependencies and process integrity remain
trusted. Existing core digest/require and strict JSON routines are reused.

`deliver_supplied(path, wake, responses, expected_digest=..., now=...)` is the pure
input harness plus local persistence. `deliver_readonly(path, wake,
expected_digest=...)` obtains actual responses via the existing collector's private
raw-response port under the writer lock. Its public `collect` behavior remains
unchanged. Neither function owns or invokes any dispatch/mutation API.

Wake fields are exactly `id`, `head`, `scheduled_for` (finite UTC epoch seconds).
IDs use 1–64 ASCII alphanumeric/dot/underscore/hyphen characters and begin with an
alphanumeric. The idempotency domain is one disposable harness identity, pinned
head and wake ID. The complete wake digest also binds its scheduled timestamp.
Reusing an ID with different content rejects. Different IDs represent different
caller-assigned deliveries; this is not a durable global scheduler deduplicator.
The caller must preserve the same ID across retries of one delivery.

A fresh wake must be no older than 300 seconds and not future, both before and
after retrieval. Each source is independently freshness/identity checked by the
accepted GitHub normalizer. Unknown CI produces only a request-evidence dry run;
unavailable or malformed/mismatched/stale sources reject without consuming a wake
or writing a receipt. This harness does not automatically retry blocked sources.

Every delivery acquires an exclusive same-path lock, rereads/validates state, then
checks durable replay **before** any source read. A duplicate returns the original
receipt with effective_decisions=0, even after restart or clock expiry. It neither
refreshes old evidence nor claims a new decision. For new wakes, content CAS must
match the current checkpoint. One receipt and wake consumption commit together via
same-directory tempfile, flush/fsync, atomic replacement and JSON readback.

Receipts contain the exact wake digest, input-checkpoint digest, previous receipt
hash, sequence, implementation hashes, source mode, sanitized source observation,
dry-run decision and recorded time. Both dispatch_authorized and
actual_scheduled_execution are always false. Chain, count and policy mismatches
reject. The hashes detect inconsistent bytes; they are not authenticity signatures
against a malicious actor capable of rewriting and rehashing the whole local file.

`source_mode: actual-readonly-gh` records the port that actually performed GETs.
The nested observation deliberately retains the normalizer's supplied-payload
label: normalization alone is not transport authentication. Raw response bodies
are kept in memory only; normalized public metadata and raw-response digests may
be persisted. The prior collector's local CLI/HTTPS/clock trust limitations apply.

## Failure and recovery

- Failure before replace leaves prior checkpoint bytes intact and no receipt.
- A lost acknowledgement after replace is uncertain until reread; retry returns
  the already committed receipt, without a second decision.
- A process crash may leave a lock and temporary file. The old checkpoint remains
  intact in the tested pre-replace crash. Further deliveries fail closed. There is
  no automatic stale-lock reclamation: an operator must verify process retirement
  and inspect state before recovery. No completion is invented.
- Concurrent writers cannot acquire the same lock. All writers must honor this
  protocol; it is local-filesystem coordination, not an OS security boundary or
  distributed lease. Use disposable local storage, not synchronized/network state.
- Keep original private checkpoints unchanged. This schema is not an upgrade path
  for objectives-status.json or the canonical worker-task schema.

## Verification and next gate

Run `python -m unittest orchestration.handoff_loop.test_core orchestration.handoff_loop.test_adversarial orchestration.handoff_loop.test_synthetic_adapter orchestration.handoff_loop.test_github_readonly orchestration.handoff_loop.test_dry_run -v`.

The 14 harness tests include normal/new/repeated wake delivery, a real subprocess
restart, a forced pre-replace process exit, lost acknowledgement after commit,
two concurrent writers, malformed wakes, CAS conflicts, stale/inconsistent input,
unknown/failed CI, and exact GET-only composition. Mocked source tests are not
evidence of real retrieval or dispatch. All previous evaluator/adapter tests run.

`dry-run-evidence.json` is the separate actual-read pilot: a simulated wake used
real GitHub metadata at the recorded source SHA, committed one disposable receipt,
then replayed in-process and after a new Python process. It records exact hashes,
source IDs/times/revisions, receipt identity and unchanged-byte checks. The temporary
checkpoint was discarded after readback. No raw response, private path, session
identifier or original checkpoint content is published. A new code head does not
retroactively change this historical source revision.

Next bounded acceptance: Dot independently verifies the exact published harness
head, restarts the disposable replay, tests interruption/concurrency and inspects
the zero-authority actual-read receipt. Future operational continuation still
requires independently verified local ownership/lease/approval observations and
an enforced dispatcher/scheduler integration owned by the existing controller.
Passing this dry run does not authorize those effects.
