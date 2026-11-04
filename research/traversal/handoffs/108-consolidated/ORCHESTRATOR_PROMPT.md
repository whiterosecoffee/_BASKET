Apply the following procedure to the current conversation. Derive its identity, purpose and receiving destination from the available evidence; do not require a manually supplied conversation ID, mission, ticker, repository or owner.

1. RECOVER THE ACTUAL CONTEXT

Review the full available conversation, including user corrections, evolving objectives, decisions, assistant proposals, authorizations, executed actions, tool results, failed attempts and unresolved commitments.

State coverage limits. Do not claim access to hidden messages, unavailable conversations or external systems. Use relevant connected context when necessary; distinguish retrieved excerpts from a complete transcript.

Infer:
- the original objective and latest controlling objective;
- required deliverables and their consumers;
- authorized scope, ownership and constraints;
- applicable completion and transfer criteria;
- repositories, components, issues, branches and receiving owners, if present.

Distinguish explicit instructions, accepted decisions, recommendations, assumptions and superseded requests. A newer instruction changes the affected scope; it does not automatically cancel unrelated obligations. Do not revive abandoned proposals as required work.

Do not ask the user to restate facts already available. If ambiguity affects implementation or authority, perform independent work first and ask at most one focused question when genuinely necessary.

2. ESTABLISH A BOUNDED OBLIGATION LEDGER

For each material deliverable record:
deliverable → controlling instruction → owner → state → evidence → unmet criterion → smallest next action.

Use distinct states for proposed, recorded, implemented, locally tested, independently verified, integrated, deployed and operationally observed.

Separate:
- required work to complete this conversation;
- external prerequisites and transferred work;
- optional improvements or research;
- superseded, rejected and explicitly out-of-scope work.

Derive acceptance criteria from the actual objective. Do not equate completing a handoff with completing the feature, or an unrelated project backlog with an obligation of this conversation.

Reuse verified evidence. Refresh only where source age, changed implementation or dependency state could materially change the next action or disposition. Label earlier checks as earlier checks.

3. DISCOVER EXISTING CAPABILITIES AND EXECUTE SMALL WINS

Where repository work is relevant, consult current applicable instructions, ownership and the specific existing issues, branches, code, contracts, tests and runbooks needed for this scope.

Compare requested behavior with actual implementation, not titles or prior summaries. Identify existing capabilities before proposing replacements. Inspect exact source revisions and relevant checks when making implementation or verification claims.

Classify work as reuse, extend, repair, integrate, consolidate, transfer, defer, discard or justified no action.

Finish authorized, unblocked work within ownership before handing it off. Prefer an existing task and implementation surface. Do not turn a review into project-wide stabilization or create duplicate engines, stores, frameworks, issues, branches, documents or schedules.

If an existing owner controls required files, use its receiving path or request a concrete ownership decision. Do not silently overwrite another owner's work. Follow applicable merge, release, spending and external-action authorization.

When blocked, identify the precise failed prerequisite and continue independent work that remains useful. Synthetic tests may advance while real inputs are unavailable; they do not establish historical or operational acceptance.

4. EXTRACT MATERIAL PROJECT INTELLIGENCE

Preserve insights at both transferable and concrete levels. For each material knowledge unit include the fields needed for independent reuse:
- Problem/trigger: the recurring need, failure or opportunity.
- Principle: the rule that generalizes.
- Pattern/mechanism: how it works, including causal links.
- Methodology: ordered steps, invariants, decision criteria and recovery.
- Concrete application: the component, episode, instrument or consumer.
- Architecture: source of truth, black-box inputs/outputs, state, dependencies, owners and consumers.
- Evidence/falsifiers: source and revision, observations, negative cases, uncertainty and conditions that would overturn the conclusion.
- Decision record: selected approach, rejected alternatives, trade-offs and reconsideration conditions.
- Destination/adoption: existing artifact or owner and whether recorded, accepted, implemented or verified.

Do not reduce substantive reasoning to theory tags or three generic bullets. Do not force every field onto routine facts.

Use prior-art families where they explain a mechanism: contracts, modularity, ports/adapters, event sourcing, state machines, idempotency, point-in-time logic, provenance, dependency graphs, falsification, reproducibility, observability, decision theory and other relevant families.

Explain applicability and limitations. Distinguish conceptual analogy from a sourced historical claim. Use primary references when external technical claims need verification. Reuse existing project vocabulary; propose taxonomy additions only when useful, without automatically creating work.

Retain failed approaches, counterexamples and negative findings that prevent repeated mistakes. Keep hypotheses separate from approved rules and verified facts. Preserve sensitive information only in its designated system.

5. AUDIT EXECUTION AND OVERLAY CORRECTIVE ACTIONS

Score observable execution 0–5 on:
objective control; execution conversion; reuse; ownership; verification; dependency handling; resource efficiency; knowledge extraction; handoff quality; closure discipline.

Use N/A for unsupported dimensions; show the calculation and evidence supporting material deductions. The normalized result is a retrospective judgment, not a completion percentage, productivity measurement or amount of missing functionality.

For every material shortfall map:
observed behavior → contemporaneously feasible better behavior → root cause or hypothesis → smallest corrective action/probe → existing owner → acceptance evidence → status.

If causation is uncertain, define a bounded discriminating probe, its decision criterion and what each result would change. Do not present speculation as a proven cause.

Prioritize correctness, data integrity and unsupported operational claims regardless of aggregate score. Avoid hindsight bias and do not penalize external blockers as worker failures.

Explicitly distinguish:
- knowledge captured;
- correction proposed;
- correction assigned or accepted;
- correction executed;
- correction independently verified.

Preserve the original retrospective score. Report subsequent improvement evidence separately; do not raise it because a prompt was written, an issue posted or a recommendation accepted.

Do not create tasks merely to recover lost points. Explain justified defer/no-action decisions. Never invent token usage, cost, duration or savings. Estimate effort/coordination only when useful and label uncertainty.

6. RECONCILE AND MATURE THE EXISTING PROJECT

Map material findings to existing capabilities, contracts, tests, runbooks and owner decisions. Resolve contradictions with evidence; unavailable source means unknown, not false.

Prefer the lowest-complexity change meeting the requirement. Explain why a broader alternative is unnecessary. Separate component correctness, composition, historical validation, predictive calibration and production operation when applicable.

Prioritize a small number of actions by user value, correctness, reusability, evidence, feasibility and risk reduction. Do not let optional research become an accidental prerequisite.

For each retained finding specify:
existing destination → required change or probe → owner → acceptance → adoption status.
Record why other findings are already incorporated, deferred or discarded.

When a base prompt or workflow caused the failure, propose a precise behavioral change to the existing owner. Include:
observed failure → old behavior → corrected behavior → regression/pilot → expected evidence → compatibility effect.

Use representative available cases, including negative cases. A supplied-evidence evaluator does not prove automatic transcript understanding, complete extraction or real-world effectiveness.

Repeated invocation must be incremental: retain the previous obligation ledger and review, refresh changed evidence, add new findings and report the delta. Do not restart inventories or reproduce unchanged documents without a reason.

7. CONSOLIDATE AND VERIFY THE ARTIFACTS

Persist material new knowledge and authorized corrections using existing conventions and ownership. Reuse the authoritative record rather than scatter competing summaries. Preserve revisions and historical evidence.

When a repository push is requested, commit the actual artifact on an authorized branch and verify its readback/diff. An issue comment is not a committed file. Report exact paths and revisions and distinguish branch publication from main integration.

Tests must challenge the contract, including invariants, counterexamples, missingness, boundaries and recovery where relevant. Passing tests do not establish untested behavior. Verify that claimed CI actually executed the required suite at the relevant source revision; shared green checks alone are insufficient.

Record actual commands/results and evidence locations. Preserve failures and correction lineage. Do not claim recipient action, adoption or operational readiness from a link or handoff alone.

8. PRODUCE ONE CONSOLIDATED HANDOFF WHEN NEEDED

If required work or material external corrections remain, produce one complete, self-contained, ready-to-paste block—even if the source conversation otherwise qualifies for archive.

Derive its destination and mission from the recovered conversation. Include:
- receiver, authority, existing repository/issue/branch/component and last verified revision;
- actual objective, scope and acceptance;
- completed work and reusable resources;
- material principles, mechanisms, methodology and architectural interfaces;
- decisions, rejected alternatives, failure lessons, assumptions, limitations and falsifiers;
- concrete corrective actions/probes, existing owners and evidence requirements;
- dependency order, blocked versus independently executable work;
- exact next executable action, verification and closeout conditions.

Do not make the receiver reconstruct essential instructions from surrounding chat or links. References supplement a self-contained block. Mark handoff generated, posted, accepted and executed separately.

If the user requested the prompt in chat and the repository, provide identical content in both and verify persistence. Do not create multiple competing prompts for the same receiving action.

If no work or knowledge needs transfer, state the evidence-backed no-action disposition rather than manufacture a handoff.

9. DETERMINE CLOSURE AND REPORT

Verify:
- all requested deliverables were supplied;
- required local acceptance has evidence;
- no executable authorized local task, pending decision or promised follow-up remains;
- material knowledge is preserved with a disposition;
- external work has an existing owner and a concrete action/probe or accepted defer decision;
- required transfer is accepted, or the user explicitly accepted transfer preparation as the endpoint;
- claims distinguish proposal, execution, verification, integration and operation.

External prerequisites do not prevent local closure unless resolving them belongs to this conversation's objective. A low execution score alone does not block archive. An unfulfilled local deliverable does.

Report concisely:
- disposition and completion scope;
- actual changes/checks and verification limits;
- execution score with material deductions and corrective-action status;
- compact knowledge/destination map;
- external owner/blocker where applicable;
- the single consolidated copy block when required;
- exactly one next action.

Select one final standalone disposition and put nothing after it:
Continue here
Decision needed
Hand off before archiving
Ready to Archive

Do not imply archiving has occurred or claim project completion from conversation closure.
