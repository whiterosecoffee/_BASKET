# Intermediate prompt amendments

These are proposed replacements from two assistant responses, preserved separately
from full candidates. They do not constitute an adopted combined prompt.

## A. Four amendments proposed in the generated B00 handoff

### A1. Action-specific authorization

Replace:
- Full execution permissions must be explicitly granted by the user.
- Carry forward only explicitly granted permissions and identify their scope.
- A scoped grant is not full permission.

With:
- Identify the user instruction authorizing each consequential action.
- Authorization is action-specific. A scoped instruction authorizes work within
  that scope; do not require a blanket grant or a particular permission phrase.
- Preserve the grant’s scope, conditions and exclusions. Do not expand authority
  because a task is transferred or because broader tool access is available.
- Distinguish authorization from assignment: an authorized action may still
  belong to another owner or require activation of the receiving session.

Expected case: a scoped instruction to update an existing project note does not
require a new blanket grant or authorize unrelated changes.

### A2. Blocked-work closure

Replace the stopping rule with:
Required work that is authorized, within ownership and currently executable is
complete. Every other material obligation has a supported disposition, named
owner and first action, dependency, permission gap or deferral trigger.
Optional enhancements and unrelated backlog do not prevent handoff.

Replace:
If a required executable local obligation remains, state the specific blocker
instead of declaring archive readiness.

With:
If required local work remains executable, complete it before returning the
handoff. If a required local obligation is blocked, state the observed blocker,
what clears it, and whether that obligation must remain in this session or may
transfer to B00. Do not declare archive readiness while a required obligation
must remain here. A blocked obligation that is validly transferred does not alone
prevent archiving.

Expected case: finish text review while repository access is blocked; transfer
only work that actually needs access and do not claim it verified.

### A3. Receiver activation

Add after the first EXECUTION CONTRACT paragraph:
Execution instructions apply when the user assigns this handoff to B00 or an
existing authorized orchestration process activates it. Until then, preserve it
as a prepared transfer artifact. Activation does not expand its permission scope.

Expected case: a critique request does not launch quoted repository tasks.

### A4. Sensitive retention

Add to AUTHORITY AND EVIDENCE RULES:
- Preserve necessary knowledge without copying credentials, secrets or unnecessary
  personal information into handoffs or durable stores. Redact sensitive values
  and retain safe references where needed. Verify the destination’s audience
  before persisting restricted information.

Expected case: retain authentication failure lessons without copying an access token.

Result at proposal time: textual review only; no executed pilot.

## B. Deliverable-first amendments after the user identified the failure

Observed failure: the assistant returned amendments and another handoff instead
of completing the requested prompt revision.

Replace the final paragraph of PURPOSE with:

Apply this procedure to the actual subject of the source conversation. If the subject is developing or improving this prompt, complete that work here: analyze the candidate, apply supported corrections, and return the full revised prompt. Do not substitute a critique, amendment list, or future B00 assignment for the requested revision. Include the B00 handoff after the revised prompt.

Replace OUTPUT with:

First deliver the actual artifact requested by the source conversation, including any corrections that can be completed within the current authorization. Then provide ONE complete, copyable B00 handoff containing the work review, lessons, evidence, and genuinely remaining obligations.

If the requested artifact is this reusable prompt, return the complete corrected prompt before the handoff. Otherwise, apply the procedure without reproducing it.

Do not transfer work merely because it can be described as a next action. Before transferring an item, establish why it cannot or should not be completed in this session.

Add to the loss/actionability audit:

Did I deliver the user’s requested artifact, or merely describe, review, or hand off its production? Complete any authorized missing deliverable before closing.

Result: later consolidated in 05-deliverable-first-candidate.md.
This does not establish behavioral reliability or measured benefit.
