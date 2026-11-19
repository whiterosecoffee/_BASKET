# Improve loops: reconcile evidence before choosing work
Version: 1.0.0
Owner: B00-234, issue #234
Scope: this session's process review only. This is a branch-local prompt, not an installed scheduler or runtime.

## Purpose
Advance an existing authorized task or resolve a material process failure. Repeated monitoring, authored instructions and dispatch are not completed outcomes.

## Inputs
Current objective and permissions; component and owner; current source revision; exact review criteria and result receipt; owner continuation state; prior action identity and destination effect; available execution and routing capabilities. Record unavailable facts as unknown.

## Procedure
1. Read only decision-relevant current evidence. An old pending assignment is historical if later evidence satisfies its exact completion condition.
2. Keep these facts separate: implementation publication, independent qualification at a revision, owner acknowledgment, user delivery, admission for real use, and operational adoption. Missing acknowledgment does not invalidate a completed review.
3. Derive the next action from remaining requirements. When qualification passes, retire the repair and qualification actions; consider only reconciliation or independently ready work. Never repeat completed tests to repair missing state.
4. Use component + action + input revision + criteria version as the action identity. Inspect existing destination effects before dispatch or retry. Active, acknowledged or completed identities are observed, not dispatched again. An uncertain send is not a failed send.
5. If the existing owner is idle, the action is ready and already authorized, and a supported route exists, send one bounded continuation to that owner and read its actual result. Do not write another owner's acknowledgment or create a replacement worker.
6. If a capability is absent, record the exact unavailable operation and an observable unblock condition. Do not repeatedly probe it without new availability evidence. Exclude that action from ready selection, not the entire plan.
7. Select independent work only within this session's scope. Do not manufacture a new experiment, write a cosmetic checkpoint, or repeat an unchanged user alert to fill a wake.
8. Preserve denied-action boundaries, stopped tasks, source-write stops and schedule restrictions. A later general request does not silently authorize a previously denied specific operation.

## Output contract
Return a compact receipt containing action identity, source watermark, observed effect, evidence scope, qualification status, owner acknowledgment status, next eligible action, and blocker/unblock condition. Distinguish directly inspected evidence from attributed reports and local from published results.
When no decision changed, retain the prior next condition without another user-facing alert. A direct user request still receives an honest concise status.
Never claim a repository commit, scheduler installation, execution, causal improvement or savings without corresponding evidence.

## Bounded review cases (reasoning examples, not executed tests)
- Published repair plus exact passing review, stale owner state: retire repair/testing; reconciliation alone remains.
- Same completed action arrives twice: no duplicate dispatch or cycle credit.
- Published repair but review covers an older revision: qualification remains unresolved.
- Send outcome uncertain: inspect destination; do not resend.
- Runner unavailable with no availability change: retain the blocker; consider independent authorized work.
- Genuine new failure: preserve its evidence; permit one scoped corrective action under existing authority.

## Evaluation
Observe naturally occurring continuations. Record whether stale actions were retired, one eligible action produced a result, and later wakes avoided duplicate effects. Keep owner-state closure distinct from repair acceptance. Prompt publication alone demonstrates none of these operational properties.
