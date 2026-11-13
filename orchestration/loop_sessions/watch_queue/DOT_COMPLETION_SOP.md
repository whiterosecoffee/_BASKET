# Turn completion to DOT — SOP adoption candidate v1

Owner: B00-235. Scope: this observer's protocol proposal.
Status: adopted for this observer's completion responses; shared/core adoption pending existing B00 protocol/template owners. This is not installed transport or a new canonical schema.

## Core rule
Every actionable worker turn ends with a completion receipt addressed to DOT, including blocked, failed, interrupted-with-recovery and no-change outcomes. Turn completion does not mean objective completion. DOT reconciles the receipt and records one next disposition against the existing objective.

Reuse orchestration/WORKER_PROTOCOL.md and basket.worker_resolution@1 for substantive repository outcomes. Do not add unrecognized fields to that schema; transport metadata below is a separate envelope proposal. Preserve current user direction over stale per-conversation allocation language: resume the existing objective and owner.

## Worker closeout
1. Re-read current steering and relevant authoritative target state. Preserve source cutoff and unavailable ranges.
2. State the outcome delta, exact branch/head or artifact identity, checks actually executed and acceptance criteria still unmet. Separate producer report, independent review, CI, integration and operational evidence.
3. Persist evidence only to an authorized destination when required; verify readback. Link the existing resolution/artifact. No-change monitoring needs a compact receipt, not a new public commit.
4. Identify one existing next owner, exact next action, required evidence and unblock condition. Reconcile renewed authority with the exact denied operation and uncertain effects; do not convert historical denial into a permanent global prohibition.
5. Return the receipt through the existing parent completion channel. Where the platform automatically notifies DOT on final response, use that route once; do not additionally send the same completion.
6. Record only observed delivery state. A final response is submitted, not proof DOT read it. If transport is unavailable, retain the receipt and report the exact delivery limitation. Do not launch a replacement worker.
7. For partial failure, return completed work, failed action/target/reason, uncertain effects and safe recovery boundary. Never wait silently for perfect completion.

## Minimum completion envelope (proposal, not a canonical schema)
- receipt_id: stable existing task/run identifier plus result revision
- recipient: DOT (private routing identifiers stay private)
- owner and objective/task reference
- run_id and checked_at; null when unknown
- outcome_state: monitoring_only | ready | working | awaiting_evidence | awaiting_approval | blocked | tested | accepted
- delta and source watermark
- evidence: exact revisions, links, execution class and test outcome
- remaining gates and unavailable ranges
- next_action: existing owner, action, acceptance condition
- checkpoint: location/revision or explicitly conversation-only
- delivery: submitted | acknowledged | uncertain; acknowledgement reference only when observed

Keep evidence dimensions separate: accepted means only the named bounded criteria, never implicit integrated/operational success.
Public artifacts must exclude private conversation IDs, paths, raw datasets, credentials and transcript text.

## DOT receipt reconciliation
1. Read the complete receipt; deduplicate by receipt_id AND payload identity. Same ID with different content is a conflict, not a duplicate.
2. Verify source freshness/head and evidence needed for the next decision. Acknowledge receipt separately from accepting claims.
3. Record accepted, rework, deferred or blocked with exact reason and one next action. Preserve failed and superseded evidence.
4. Update the existing authorized private objectives checkpoint, if its path/owner is established; validate and read back. If unavailable, record that gap without inventing a second authoritative status file.
5. Continue authorized ready work with its existing owner. Never infer execution from dispatch or create competing owners.
6. Notify the user only for material outcome, changed decision or actionable blocker. Keep unchanged monitoring receipts internal.
7. If delivery acknowledgement is absent, inspect existing turn/receipt state before retry; repeated wake must not replay completed work. No new timer or retry schedule is introduced by this SOP.

## Immediate handoff from this observer
Existing FETCH published placement completion at 8cf8897689cc69f41fe9b68a8125e6592d84d653. DOT's next action is to obtain the existing consumer/route owner's read-only NVDA resolver readback with exact file identity and explicit coverage/basis limits. This observer verified the published owner report, not private filesystem placement. Do not repeat relocation merely to obtain acceptance.
PR266 repair remains with B17-265. Projection acceptance remains with #261 and adoption with #230. These independent gates do not block recording successful placement evidence.

## Shared adoption path and acceptance
Existing B00 protocol owner reconciles this procedure into WORKER_PROTOCOL.md; #201 updates governing entry instructions; #243 applies the completion slot to templates; #169 retains closeout/receipt tooling; #105 independently checks the combined behavior. These are proposed receiver responsibilities, not claims of dispatch or acknowledgment. Do not modify another owner's files from this proposal.

Required validation before claiming core adoption:
- successful task: one receipt, exact evidence, DOT disposition and next existing owner
- no-change wake: internal receipt, no user alert or duplicate public write
- blocked action: exact target/reason/unblock; unrelated work remains eligible
- duplicate delivery: one disposition and no repeated effect
- same receipt ID/different payload: conflict preserved
- uncertain publication: readback before retry; no fabricated success
- stale/wrong-head green CI: no acceptance promotion
- newer user correction: preserved and reconciled with exact action
- DOT acknowledgement without acceptance: distinct states
- private destination unavailable: explicit gap, no public substitute or second authority

Validation status: documentation review only; no transport or runtime tests executed here.
