# Initial execution-contract amendment

Origin: assistant response to "Score the response output and determine what needs
to change in the handoff prompt." This is an amendment proposal, not a complete
prompt or a generated task assignment. Formatting is normalized from chat.

## Execution contract

Produce ONE self-contained B00 handoff that instructs the receiver to execute all remaining work already authorized by the user. Do not frame authorized work as optional recommendations or require renewed permission merely because responsibility is transferring.

Carry forward the exact authority boundary: permitted actions, prohibited actions, ownership, and any actions requiring separate approval. Never infer implementation, policy-adoption, merge, release, or external-communication authority from the existence of a handoff.

For every remaining obligation, state:

- The required outcome and why it remains necessary.
- Its owner, existing destination, dependencies, and authorization status.
- The first executable action and acceptance evidence.
- Its disposition: execute now, blocked by a named dependency, or deferred until a specific trigger.

The receiver must refresh relevant state, execute unblocked authorized work, verify results, and persist findings in existing authorized destinations. Continue independent work while a dependency is unresolved. Ask only for missing information or authority that materially blocks a specific action.

## Durable knowledge

Preserve and store both positive and negative lessons, including useful knowledge from completed work. Each material lesson must include the observation, supporting evidence, causal explanation or uncertainty, the method to repeat or avoid, its applicable limits, and its durable destination.

Distinguish demonstrated lessons from hypotheses. Record failures and subsequent recovery together; successful repair does not erase the failure. Do not store unsupported generalizations, duplicate existing knowledge unnecessarily, or create new systems where existing artifacts suffice.

## Completion and transfer

Keep the scored work attempt, failures, improvements, completed knowledge, remaining obligations, and mutation/cleanup inventory inside the single copied artifact.

Before returning it, audit whether the receiver can act without recovering material context from the source conversation. Confirm that every obligation has a disposition and every material lesson has either a storage location or an explicit remaining storage action.

Report execution, verification, storage, and blockers separately. Never claim that generating a handoff establishes receipt, persistence, acceptance, adoption, or completion.

## Workstream-specific command proposed in that response

B00: Execute the remaining authorized review and reconciliation for #169/#170. Retrieve the existing HANDOFF_PROMPT.md and the complete candidate, compare their binding rules, and produce an exact proposed revision. Preserve the existing test evidence and its limitations. Capture positive and negative lessons in the existing authorized knowledge destinations; where persistence is not authorized, include the complete proposed update and identify the precise authorization needed. Do not implement, adopt policy, merge, tag, release, or launch another worker under this handoff.
