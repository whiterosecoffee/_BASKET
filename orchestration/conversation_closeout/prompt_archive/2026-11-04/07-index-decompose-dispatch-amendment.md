INDEX, DECOMPOSE AND DISPATCH

Use a shallow first pass to decide what deserves further review.
Do not run every specialist by default.

1. INDEX

Identify consequential:
- Requirements and commitments.
- Completion claims and verification evidence.
- Decisions and architectural boundaries.
- Useful findings and repeatable methods.
- Failures, recovery and unresolved cleanup.
- Ownership, authorization and dependencies.

Give each indexed item a stable ID and source pointer.
Record missing evidence without reconstructing unavailable history.

The index is a routing aid, not a complete retrospective.

2. NORMALIZE INTO UNIQUE WORK ITEMS

Consolidate repeated expressions of the same requirement.
Preserve distinct constraints and conflicting statements.

Split compound items only when their outcomes, ownership, dependencies or
acceptance checks differ.

Each unique item must have:
ID | outcome or review question | source pointers | evidence state |
scope | dependencies | intended output

Do not invent implementation tasks from optional ideas.
Do not split work merely to increase parallelism.

3. SELECT REVIEW WORKERS

Activate only workers supported by indexed evidence:

REQUIREMENTS REVIEW
Trigger: multiple obligations, changing objectives or compound requirements.
Output: canonical requirements, missing obligations and acceptance criteria.

EXECUTION BACKCHECK
Trigger: material completion claims, tool activity or uncertain results.
Output: supported execution assessment, evidence gaps and verification tasks.

KNOWLEDGE AND LESSONS
Trigger: reusable discoveries, consequential decisions, failures or recovery.
Output: positive/negative lessons, mechanisms, limits and storage instructions.

ARCHITECTURE AND CONTRACTS
Trigger: multiple capabilities, shared interfaces or cross-owner dependencies.
Output: capability boundaries, input/output contracts and integration sequence.

SCOPE AND COLLISION REVIEW
Trigger: repository mutations, concurrent work or uncertain ownership.
Output: allowed paths, collisions, branch/workspace allocation requirements
and prohibited targets.

The coordinating reviewer handles routine items directly.
Combine roles when their evidence overlaps and separate workers add little value.

4. ASSIGN NARROW REVIEW CONTRACTS

Each worker receives:
- The exact review question.
- Assigned item IDs and relevant source excerpts or retrievable pointers.
- Relevant repository and authority context.
- Read/write restrictions.
- A token or effort budget where supported.
- Required output fields.

Review workers must not implement, post externally or launch other workers
unless their assignment explicitly includes those actions.

Worker return contract:
item ID | finding | evidence | uncertainty | concrete action |
positive/negative lesson if material | destination | dependency

Workers return findings to the coordinator.
They do not independently produce competing final handoffs.

5. CONTROL COST AND DUPLICATION

Use the first pass to estimate whether a specialist review is worthwhile.
Spend deeper analysis on consequential uncertainty or reusable value.

Do not send every worker the entire conversation when a bounded evidence packet
will suffice. Include enough context to avoid misleading extraction.

Parallelize independent reviews.
Sequence reviews where one establishes another’s inputs.
If worker tools are unavailable, perform the selected roles sequentially.

Create branches/worktrees only for authorized repository mutation.
Conversation review alone does not require repository isolation.

6. RECONCILE AND HAND OFF

The coordinator must:
- Merge duplicate findings under canonical item IDs.
- Resolve contradictions with evidence or preserve them as unresolved.
- Ensure each required action has one accountable owner.
- Separate review findings from execution assignments.
- Include completed knowledge and lesson-storage requirements.
- Produce ONE portable handoff with scoped execution packets.

Do not stop at specialist recommendations.
Convert supported findings into concrete execution instructions, explicit
decisions or supported defer/discard dispositions.

Do not claim workers ran when only assignments were prepared.
