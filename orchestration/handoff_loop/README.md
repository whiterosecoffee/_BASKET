# Handoff loop: first bounded increment

Draft `basket.handoff_objectives@0.1-draft`; B00 component under existing
[issue #169](https://github.com/whiterosecoffee/_BASKET/issues/169).
Exclusive scope: `orchestration/handoff_loop/**`. Parent branch: main;
base: `74d913e8913d630d85451344689e093aeea07efc`.
Branch: `work/169-handoff-loop-20261112`. No overlap found in the checked open
PR paths or local worktrees. This observation is not a perpetual ownership lease.

This library evaluates a supplied, independently verified observation and a
resumable snapshot. GitHub issues/PRs remain authoritative; this is not a queue,
replacement worker-task schema, scheduler, transcript scraper or launch service.
The schema is explicitly draft and its executable validator is `core.validate`.
`objectives-status.example.json` is synthetic, not a current worker registry.

Reuse the existing closeout CLI, rather than adding another:
`python -m orchestration.conversation_closeout --input evidence.json --output closeout.md`.
Its source and richer HANDOFF_PROMPT.md were inspected at
`06a7f0a1b197400f48b0317529c4184d48efe142` on
`work/169-conversation-closeout-cli` (PR #170). That dependency is not copied or
merged into this main-based branch. Retrieve it read-only when closeout is needed.

## Input and trust boundary

`evaluate(state, observation, receipts, now=...)` returns one action plus separate
dispatch, execution, publication, acceptance and delivery dimensions. Actions:
coalesce, continue, request checkpoint, handoff-ready, blocked, no-change.
Continuation retains the exact owner/session/branch/worktree/scope. Offline or
unknown/stale observation parks execution. Pending approval is not inactivity.
Unchanged blocker fingerprints and duplicate wakes produce no retry. All activity
flags must be explicitly observed. No automatic archive or replacement launch.

The **caller** verifies actual environment/hostname, current exclusive ownership,
activity, permissions and data access, then supplies timestamped observations.
The caller also builds the receipt map from independently verified sources. Never
deserialize that trusted map out of the status file. References absent from this
map, stale artifact revisions and session-start acknowledgements are rejected.
Acceptance receipts bind objective and criterion IDs. This kernel cannot detect a
lying trusted adapter or authenticate a supplied receipt; production adapter and
launch enforcement remain gaps. Tests use synthetic receipts, not real acceptance.

Objectives carry stable IDs, parent, dependencies, owner, scope, status, evidence
references, artifact revisions, acceptance conditions, blockers and next action.
Hierarchy/dependency cycles and dangling/duplicate references fail. Accepted parents
require accepted children/dependencies and bound acceptance evidence. Starting a
session cannot satisfy acceptance. Do not equate passing structural validation
with semantic source completeness or human acceptance.

Coverage keeps verified read watermark separate from persisted ranges and unknown
ranges. Incrementally read only available changes after the watermark. Never mark
inaccessible conversation ranges covered; no repeated full transcript scrape.

## Persistence and recovery

Keep actual `objectives-status.json` and ownership registries outside Git.
Bootstrap a new private checkpoint only after verifying there is no existing file
or active writer, using exclusive creation, flush and readback. Subsequent writes
must use `persist(path, expected_digest, update, receipts, observation, now=...)`:
exclusive lock, current reread, content CAS, admitted owner, revision increment,
validation, same-directory temporary file, fsync, atomic replace, readback.
Duplicate wakes do not invoke update or rewrite. Claims cannot be transferred
through this writer. All writers must honor the lock; it is not an OS security
boundary or a distributed lease. Avoid network/synchronized filesystem checkpoints.

An interrupted pre-replace write preserves the old checkpoint. A process crash may
leave a lock/temp file: stop and have the operator prove retirement, inspect the
checkpoint and recover explicitly. Never expire or delete a lock automatically.
Post-replace failure means outcome uncertain: reread before retry. Handoff readiness
requires old writer retirement plus replacement acknowledgement of branch, scope,
data access and outstanding task. Readiness does not perform ownership transfer.

## Bounded manual test

From the branch root: `python -m unittest orchestration.handoff_loop.test_core -v`.
This exercises deterministic decisions and real temporary-file writes, interruption,
CAS conflict, duplicate replay and lock contention. It neither dispatches work nor
proves scheduler/session durability. See SCHEDULER.md and methodology-gaps.json.

Next: independent adapter/launch integration review, and exact-session hourly routing
verification by the controller. Shared protocols and CI remain with existing owners.
