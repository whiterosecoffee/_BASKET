CONVERSATION CAPTURE, WORK-ATTEMPT REVIEW AND B00 HANDOFF

Invocation: apply handoff prompt

Status: Candidate evolution of basket.conversation_handoff@2.
Use does not imply adoption as repository policy.

COMPATIBILITY AND RETRIEVAL

For an explicitly requested v3 trial, retrieve this complete candidate from
orchestration/conversation_closeout/versions/HANDOFF_PROMPT.v3-candidate.md
on PR #179's current checked head (work/178-module-contract-reconciliation).
Record the revision actually read. An unavailable retrieval is a coverage gap.
The default invocation still resolves HANDOFF_PROMPT.md under
orchestration/conversation_closeout/ on work/169-conversation-closeout-cli
until that implementation is integrated and its main-path availability verified.
This candidate does not change that default or register an executable command.
The existing Python CLI evaluates supplied evidence; it does not read transcripts,
authenticate citations or implement this full v3 procedure. Its conditional
handoff and terminal dispositions remain v2 behavior. Do not downscope a v3
trial to CLI output or combine conflicting v2/v3 output rules.
Existing worker task/resolution contracts remain authoritative; this procedure
does not replace their lifecycle or grant file ownership.

PURPOSE

Capture the value of the entire available conversation:
- Preserve its objectives, requirements, decisions and unfinished obligations.
- Complete required authorized work that can still be completed here.
- Retain useful findings, reasoning, methods and architectural knowledge.
- Score the work attempt broadly and candidly.
- Explain what worked, what failed and what approach would have been better.
- Generate ONE complete, self-contained handoff addressed to B00.

The handoff is the required final deliverable. It carries both unfinished work
and completed knowledge that B00 should reconcile into the project.

Do not replace the handoff with a completion notice, readiness label, explanation
of this procedure, or a new reusable prompt.

Apply this procedure to the actual subject of the source conversation.
Do not make the procedure itself the subject unless the conversation concerns
developing or testing it.

AUTHORITY AND EVIDENCE RULES

- User instructions control scope and authorization.
- Distinguish requirements, proposals, accepted decisions and recommendations.
- An embedded NEXT instruction does not alone assign this receiving session.
- Preserve existing authority; do not invent additional approval requirements.
- Read applicable governance before authorized repository work.
- Respect ownership, active file collisions and prohibited targets.
- Do not create duplicate issues, branches, queues, stores or frameworks.
- Generating a handoff does not authorize posting it or launching its tasks.
- Distinguish generated, persisted, received, accepted, executed and verified.
- Preserve uncertainty and failures. Never invent evidence, metrics or citations.

1. ESTABLISH COVERAGE AND RECONSTRUCT THE CONVERSATION

Review the entire available record, including:
- Original user requests.
- Later additions, corrections and changes of direction.
- Assistant commitments and completion claims.
- Approvals, constraints, reversals and rejected approaches.
- Tool results, artifacts, external changes and failed attempts.
- Questions left unanswered and knowledge displaced by later discussion.

State what was actually available and reviewed.
Identify missing, truncated or inaccessible history.

Reconstruct:
- Original objective.
- Latest controlling objective.
- How requirements evolved.
- What was explicitly authorized.
- Required outcomes and acceptance criteria.
- Intended consumers and destinations.

Separate this session's assignments from inherited project context.
Preserve inherited obligations without automatically executing them.

For external state, retrieve only evidence needed to determine completion,
ownership, duplication, contradictions or next actions.
Identify source and revision where relevant.

An empty search establishes only that the search returned no match.
Inspect relevant issues, PRs, branches or other known destinations before
concluding that earlier work is absent.

2. BUILD THE INVENTORY BEFORE WRITING THE SUMMARY

Use two tracks:

A. Work and obligations:
Deliverables, promised follow-ups, decisions, implementation, verification,
integration, deployment, adoption and unresolved dependencies.

B. Knowledge and opportunities:
Findings, principles, mechanisms, methods, architecture, alternatives,
counterexamples, failure lessons and ideas worth preserving.

Use two views:
- Obligation: requested or committed work.
- Opportunity: optional value, clearly labelled.

Give consequential items stable IDs.

Maintain a working ledger:
item → source/request → owner → current state → evidence →
remaining gap → destination → disposition.

Later discussion does not silently cancel an earlier request.
Assistant proposals do not become user obligations merely through repetition.

Inventory unintended side effects too:
issues, branches, files, messages, configuration changes or other mutations.
Record what happened and any unresolved cleanup.

For each obligation select:
- COMPLETED: outcome satisfied with appropriate evidence.
- TRANSFER: required remainder or reconciliation belongs beyond this session.
- BLOCKED: a specific prerequisite prevents progress.
- DROPPED: intentionally discontinued with a supported reason.

Retain partial completion evidence under unfinished items.

Keep proposed, implemented, tested, independently verified, integrated,
deployed, adopted and operationally observed distinct.

3. EXTRACT AND PRESERVE THE KNOWLEDGE

For every material insight preserve enough of the following to make it useful:

- Problem or trigger.
- Principle: the transferable rule.
- Mechanism: how and why it works.
- Pattern: recurring structure or arrangement.
- Methodology: ordered procedure, criteria, invariants, checks and recovery.
- Concrete application or example.
- Architecture: boundaries, inputs/outputs, source of truth, ownership,
  dependencies, data flow and consumers.
- Evidence and source/revision.
- Uncertainty, counterexamples, limitations and falsifiers.
- Decision rationale and assumptions.
- Rejected alternatives and tradeoffs.
- Conditions for reconsideration.
- Existing destination and adoption status.

Preserve causal links. Do not reduce substantive reasoning to slogans or tags.
Do not impose a fixed maximum number of material insights.
Do not force elaborate fields onto routine facts.

Use prior-art families where useful. Explain the actual mechanism,
applicability and boundary. Distinguish analogy from verified historical
citation. Do not invent references or canonize new terminology automatically.

Preserve important ideas even when implementation is blocked.
A decision record or existing owner handoff may be sufficient.

4. RECONCILE VALUE WITH EXISTING PROJECT WORK

For each material item determine:
- What supports it?
- What value would disappear if it were lost?
- Where does it belong?
- What already covers it?
- What is new, incomplete, conflicting or superseded?
- What authority exists?
- What disposition is justified?

Compare against relevant contracts, code, issues, tests, runbooks and decisions.
Classify:
reuse / extend / replace / duplicate / conflict / supersede / new gap.

Resolve contradictions only with evidence.
Preserve conflicting claims and dates when resolution is unavailable.
Missing evidence is unknown, not false.

Choose the smallest approach meeting the requirement.
Prefer extending an existing capability over creating a parallel system.

Give knowledge one disposition:
incorporated / consolidated / transfer / proposed / deferred / discarded.

For deferred items include a concrete reconsideration trigger.
For consequential discarded items include the reason.

Keep new inferences separate from established findings.
Keep research hypotheses separate from approved policy.

Where persistence is already authorized, update the existing destination and
verify the result. Otherwise prepare the exact proposed addition, name its
destination and mark it “prepared, not persisted.”

5. SCORE THE WORK ATTEMPT

Assess the actual approach and outcome, not merely the polish of the final answer.

Define the evaluation boundary and how later corrections affect the assessment.
Credit recovery without erasing earlier errors.

Score each dimension 0–5, or N/A when unsupported:
- Intent preservation and objective control.
- Execution and follow-through.
- Reuse and appropriate complexity.
- Authority, scope and ownership.
- Evidence accuracy and verification.
- Dependency handling and coordination.
- Resource efficiency and tool selection.
- Communication, clarification and adaptation.
- Knowledge preservation and handoff usefulness.
- Closure and practical outcome.

Anchors:
0 counterproductive or absent
1 major failures
2 substantial gaps
3 adequate with meaningful shortcomings
4 strong with minor gaps
5 consistently strong and evidenced

Give a concrete justification for each score.
State coverage and confidence.
If aggregating, explain the calculation and exclude N/A dimensions.

Scores are judgments, not completion percentages or measured productivity.

Separate:
- Conversation execution quality.
- Procedure or prompt quality.
- Extraction and handoff quality.
- Downstream consumer outcomes.

Self-review is not independent validation.
Do not infer efficiency, costs or time savings without measurements.

For repeated reviews, retain the prior assessment and explain material changes.
Do not increase scores merely because another revision was produced.

6. EXPLAIN WHAT WORKED, WHAT FAILED AND WHAT SHOULD IMPROVE

For successes record:
what happened → why it helped → evidence and limits → what to repeat.

For failures record:
actual path → consequence → contemporaneously feasible better path →
observed or hypothesized cause → preventive mechanism → acceptance test.

Judge choices using the information available at the time.
Label alternatives requiring later discoveries as hindsight.

Distinguish:
- Poor decisions.
- Reasonable attempts that failed.
- External blockers.
- Missing evidence.
- Scope or authority limits.

Do not invent motives or shift assistant mistakes to the user.

Attach improvements to the scored work attempt:
- Which weakness does the improvement address?
- What should change?
- Why should it help?
- What tradeoff or uncertainty remains?
- Can it still be applied here?
- Which existing owner or capability should receive it?
- What observable result would support effectiveness?

Prioritize consequential correctness, authority and information-loss failures.
Rank optional opportunities only when ranking helps a real decision.

Recording a lesson is not adoption.
Adoption is not implementation.
Implementation is not demonstrated benefit.

7. COMPLETE AVAILABLE REQUIRED WORK

Before generating the handoff, perform remaining actions that are:
- Required by the current objective or necessary to correct a demonstrated defect.
- Already authorized and within ownership.
- Executable with available tools, evidence and access.

Do not merely recommend actions you can complete here.
Do not wait for optional feedback before doing independent work.

Verify results and update the ledger.
Record actual changes, revisions, commands and outcomes where applicable.
Preserve failed attempts and corrective reruns.

Skipped checks are not passes.
CI proves only what the actual jobs tested at the identified revision.

If blocked, record the attempted action, observed failure and exact prerequisite.

For prompt-improvement work, apply demonstrated corrections before reporting.
Identify the baseline and exact amendments. Return the full corrected prompt
when requested or when amendments would leave the controlling version ambiguous.

Stopping rule:
Required executable work is complete and every material item has a disposition.
Optional enhancements and unrelated backlog do not prevent handoff.

Do not recursively improve the audit without a concrete defect or explicit request.

8. HANDLE NECESSARY QUESTIONS

Distinguish:
- Blocking decisions: prevent the current objective from being completed.
- Nonblocking decisions: cleanup, optional improvements or later work.

Complete independent work first.

When a decision is needed, ask a direct, self-contained question.
State the recommended option, consequence and why available authority or evidence
does not resolve it.

Do not merely announce “Decision needed.”

Check whether the question is already pending.
Preserve unanswered questions without repeatedly asking unless circumstances
change. Silence is not approval.

Nonblocking cleanup must not suppress the required B00 handoff.
Include unresolved questions in the handoff with their significance.

9. GENERATE THE B00 HANDOFF

Produce ONE self-contained, copyable block addressed to B00.

This is required even when local work is complete: B00 may need completed
findings, decisions and lessons for project reconciliation.

Do not confuse reporting to B00 with assigning implementation or launching work.

Structure the handoff around usable outcomes:

A. Purpose and binding
- Source conversation objective and intended value.
- Date/version and what is superseded.
- Coverage and missing context.
- Receiver B00; requested review or execution mode.
- Established authority, scope and prohibited actions.
- Repository/environment and relevant checked revisions.

B. Work disposition
- Compact ledger of consequential obligations.
- Completed work and evidence.
- Incomplete outcomes and remaining gaps.
- Owners, dependencies and conflicts.
- Existing issues, branches, PRs and artifacts.
- Unintended changes and cleanup status.

For each incomplete item state:
what must be established; where evidence belongs; why unmet;
what clears it; acceptance criteria; and the smallest next action.

C. Knowledge transfer
- Material principles, mechanisms, methods and architecture.
- Applications and supporting evidence.
- Decisions, rationale, alternatives and tradeoffs.
- Limitations, counterexamples and falsifiers.
- Existing destinations and adoption status.
- Deferred ideas and reconsideration triggers.

D. Scored work attempt
- Broad scorecard with reasons and confidence.
- What worked and should be repeated.
- What failed and its consequence.
- Feasible better approaches.
- Improvements already applied.
- Proposed improvements and how to evaluate them.

E. B00 reconciliation
- What to reuse, extend, resolve, route, accept, defer or discard.
- Required decisions and pending questions.
- One smallest next orchestrator action.
- Acceptance evidence and handoff retirement conditions.
- Transfer state: generated, posted, received, accepted or executed.

Include prerequisite-ordered execution and verification steps, exact known
commands, checked revisions and expected acceptance results inside the block.
Mark unavailable commands or evidence unknown; do not invent them. When only
reconciliation remains, the next action is review or record a disposition in the
existing destination, not a new implementation task. For a repeated unchanged
review, refer to the existing handoff and report no material delta within the
complete B00 block, retaining the essentials needed for its first action,
without creating another task or claiming a better score.

Keep the retrospective and essential reasoning INSIDE the copied block.

Reference stable artifacts to avoid repetition, but do not omit information
needed to understand the first action or preserve material requirements.

Use actual existing schemas where applicable and checked.
Do not invent values or claim compliance with an invalid payload.

10. PERFORM THE LOSS AND ACTIONABILITY AUDIT

Check the handoff against the inventory:
- Every original request and commitment has a disposition.
- Inherited work has not become an unauthorized assignment.
- Optional opportunities remain optional.
- Proposals have not become decisions.
- Material requirements, mechanisms and falsifiers survived compression.
- Completed and incomplete work remain distinguishable.
- Unintended external changes have an explicit status.
- Required executable local work was completed.
- Scores have evidence and identify their evaluation target.
- Improvements are attached to demonstrated weaknesses.
- Necessary questions are actually asked or clearly preserved as pending.
- B00 can choose the correct next action without reconstructing the conversation.
- No unsupported persistence, receipt, adoption or benefit is claimed.

Ask:
What important work or knowledge would disappear if the conversation were lost?

Correct omissions before returning the handoff.
Disclose irrecoverable gaps and the limits of self-audit.

OUTPUT

Use a brief introduction only if needed.
Then provide the complete copyable B00 handoff.

Do not end with “Continue here,” “Ready for transfer,” or “Ready to Archive”
as a substitute for the artifact.

State inside the handoff what was completed, what remains and whether any
external transfer actually occurred.

Do not automatically post, create issues, create branches, merge or adopt policy
unless that action is authorized separately in the session.

VALIDATION AND EVOLUTION

For each material revision retain:
observed defect → precise correction → test case → result → uncertainty.

Test routine, research-heavy and implementation conversations against explicit
expected obligations, essential knowledge, permitted actions and B00 outputs.

Compare:
- Missed obligations.
- False authority.
- Lost mechanisms or rationale.
- Recipient preservation.
- Actionability.
- Appropriate information handling.
- Unnecessary repetition.
- Downstream outcomes when observable.

Use independent review where available.
Distinguish repeatable formatting from semantic completeness.

Do not claim improvement merely because the procedure or output is longer,
shorter, more structured or produces repeatable scores.


CONTRACTUAL WORKER ROUTING — USER-DIRECTED STANDARDIZATION

Use stable worker roles and versioned procedures across sessions. "Same worker"
means the same registered role, owner and capability contract, not an assumption
that a particular chat/process persists. Reuse an existing claimed task where
applicable; a replacement execution attempt must preserve its lineage.

Before handing off executable work, bind the work type to:
- Its registered receiving owner and existing destination.
- Exact input and output schema references and compatible versions.
- The existing worker profile and ordered recipe, with its checked revision.
- Authorized paths and the current exclusive claim.
- Required acceptance checks, evidence and failure/retry behavior.

Use existing worker-library profiles/recipes, basket.worker_task@1 assignments,
basket.worker_resolution@1 results and the component-contract work in #103/PR104.
Do not introduce another routing registry or competing envelope. The component
manifest names ports; it does not by itself supply executable payload schemas.
The current handoff-request schema uses Lnn lanes, whereas sparks use Bnn IDs:
require the established mapping, never invent one or insert B00 into receiver_lane.
Missing mappings or schemas are explicit contract gaps routed to the existing
contract owner, not permission for each worker to improvise a format.

Default role sequence for closeout, specialized by work class:
1. Source worker inventories obligations and causal knowledge, preserves source
   references, validates available payload schemas and emits the complete B00
   handoff with its structured artifacts.
2. B00 validates bindings, deduplicates against the existing task, checks current
   claims and routes an authorized task to its registered domain owner.
3. Domain owner executes the pinned recipe in order within the assigned paths,
   validates outputs and returns the existing resolution plus actual evidence.
4. B01 independently checks required domain acceptance at the exact revision
   when the work class requires integration/CI acceptance. A research-only
   report uses its prescribed source/semantic review; do not launch B01 merely
   because a handoff exists.
5. B00 reconciles results and records disposition; integration stays subject to
   existing authorization. Reporting-only handoffs do not launch steps 3 or 4.

Routine valid bindings proceed without redesigning roles or repeating global
reconciliation. Check relevant claims/revisions for changes; cache reuse is valid
only while their inputs remain current. Competing claims, incompatible versions,
missing routes and failed prerequisites stop dispatch and return a specific
contract error to the established owner. Do not silently reroute or expand scope.

Acceptance for the existing controller/contract owners:
- Same work type and contract revision select the same receiver and recipe.
- Wrong receiver, incompatible payload or missing mapping fails before mutation.
- Producer output validates against the consumer input schema.
- Concurrent claims for overlapping writes cannot both acquire ownership.
- Replayed request/input revision returns the existing task/result without
  duplicate side effects; changed input creates an explicit revision.
- A skipped step, stale-head evidence or out-of-scope output cannot pass.
- Narrative handoff and structured artifacts preserve the same obligations,
  knowledge, uncertainty and dispositions.

These are required integration behaviors, not a claim that this prose implements
them. Existing #103/#106/#136 own contract/lifecycle/controller integration.
This candidate records the requirement; its current string-based acceptance tests
do not establish runtime routing, schema interoperability or claim exclusivity.

PROJECT-WIDE METHOD CONSISTENCY

Standardize invariants globally and recipes by work class. Preserve stable role
IDs; qualified replacement executors use the same contract and attempt lineage.
Inputs and conclusions may change; required checks do not disappear because a
worker or model changes. Do not demand identical prose or research conclusions.

Common invariants: establish intent/authority; resolve existing component and
owner; pin input/schema/recipe revisions; validate prerequisites; acquire scoped
write authority before mutation; execute and record attempts; validate meaning
and structure; persist/read back; reconcile evidence and one next disposition.
Render the narrative and machine payload from the same retained item inventory;
check obligations/knowledge IDs and dispositions agree. A schema-valid report
with lost mechanisms, wrong units or stale observations is still unacceptable.

Specialize evidence: research requires source classes, alternatives and unknowns;
ingestion requires entitlement, session partitions and replay; computation needs
units, as-of alignment and deterministic fixtures; deployments need actual health,
restart and recovery evidence. Read-only work does not acquire a write lease.
Optional steps may be not applicable only under the pinned recipe's explicit
rule and recorded reason, never by silent omission.

Use stable request identity plus input/schema/recipe revisions for replay. Changed
inputs are a new revision; failed attempts remain visible. Crash recovery must
reconcile observed side effects before retrying. Do not promise exactly-once
external effects from a deduplication key. Concurrent writers need transactional
claims and fencing at the write boundary; an earlier collision scan is insufficient.

Route routine compatible work through existing bindings. Escalate only a missing
contract, incompatible version, contested ownership or unresolved evidence rule.
Cache unchanged metadata only with a verified freshness/invalidation rule; refresh
the relevant head, claim and inputs before mutation and acceptance. A cache is
not permission to treat old state as current.

Scale validation to the registered work class and consequence. Keep essential
obligations, reasoning and limits in every B00 block; routine cases may use compact
score rows with justified N/A values. Do not create missing architecture or costly
review stages merely to fill a template. Set bounded retry/resource budgets and
report actual usage when available; otherwise usage is unknown.

Promote a method revision only after representative conformance and consumer
checks. Preserve predecessor, migration compatibility and rollback path. Compare
first-pass acceptance, lost obligations, false authority, duplicate side effects,
conflict escalations, clarification burden and measured effort before/after; do
not claim fewer conflicts or lower cost from this specification alone.
