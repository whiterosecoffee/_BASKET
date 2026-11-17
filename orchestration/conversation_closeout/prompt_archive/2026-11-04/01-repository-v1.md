# Retrieve Conversation Handoff — evolving on-demand protocol

**Protocol:** `basket.conversation_handoff@1` (candidate)  
**Owner:** B00 · **Existing workstream:** Issue #169 / draft PR #170  
**Invocation in any _BASKET conversation:** **Retrieve conversation handoff prompt.**

This file is the durable, copyable natural-language procedure. The offline CLI in this directory is a *supporting deterministic evaluator*, not a transcript reader or a substitute for the assistant's evidence review. This protocol is versioned independently of the Python code and remains a candidate until reviewed and integrated on main.

## Copyable full instruction

> **Retrieve conversation handoff prompt.** Review the entire conversation available to you, including latest controlling instructions, objective changes, decisions, completed and failed attempts, implementation, evidence and outstanding commitments. Determine the smallest useful closeout scope. Complete authorized work first; never use a handoff to avoid executable work.
>
> **Recover evidence:** For repository work, consult current relevant main governance, exclusive ownership, existing issues/PRs, changed files and exact-head CI only where freshness affects disposition. Do not infer active workers from open PRs. Distinguish user assertions, conversation observations, independently verified evidence, inferences, scenarios and unknowns. Report transcript coverage limitations. Never infer a test ran from a passing generic workflow.
>
> **Audit execution:** Classify each required deliverable as verified, implemented-unverified, incomplete, blocked, transferred or out of scope. Score observable execution across objective control, execution conversion, reuse, ownership, verification, dependencies, efficiency, knowledge extraction, handoff and closure (0–5 each; N/A if unavailable; normalize over observed dimensions). Separate execution quality from completion. Identify at most three material, avoidable failures using contemporaneous information: actual path → feasible better path → preventive test/pattern. Do not invent measured time/token savings.
>
> **Extract knowledge:** Preserve material principles, patterns, methodologies, component boundaries, input/output contracts, decisions and rejected alternatives, research evidence, failure lessons, counterexamples, assumptions, limitations and specific applications. Separate generalized principle from concrete use case. Use concise internal theory-family tags (e.g., DBC, HEX, DAG, EVS, CQRS, IDEM, PIT, PROV, FALS, REPRO, FSM, POST, INFO, DEC, MOD, OBS) with **no arbitrary tag maximum**. Missing or unknown tags are taxonomy-review signals, not grounds to discard an insight. For each significant architecture insight, state the theory/pattern, mechanism, applicability and boundary; do not fabricate citations.
>
> **Compare and mature:** Match each material insight against existing authoritative project capabilities and prior-art families. Determine whether it reuses, extends, duplicates, conflicts with or supersedes existing work. Prefer existing contracts, tests, runbooks, failure registers and issues over new artifacts. Rank improvement candidates by reuse, impact, novelty, evidence, feasibility and risk reduction (0–5 each) only when ranking materially helps. Disposition each insight: already incorporated, consolidated, transfer, propose, defer or discard. Never promote an untested hypothesis into canonical policy. Preserve contradiction and provenance.
>
> **Execute and consolidate:** Complete all authorized low-risk corrections, tests and durable updates inside ownership. Avoid unrelated stabilization, new schedulers, new stores, duplicate issues, unnecessary PRs, merges or releases. If an external dependency remains, use the existing owner/issue. Do not confuse posted, accepted, executed and integrated states.
>
> **Handoff requirement:** Whenever final disposition is **Hand off before archiving**, ALWAYS generate a **complete self-contained copyable orchestrator handoff prompt** even when an existing GitHub handoff exists. Include functional objective, receiving owner, repository/issue/branch/PR and last verified SHA, work already completed (do not repeat), outstanding acceptance, ownership/prohibited paths, dependency order, evidence and tests, key principles/patterns/methodologies/theory tags and their application/limits, existing capabilities to reuse, unresolved risks, one next executable action, and completion/escalation criteria. Reuse the existing receiving issue; post only if authorized and materially useful. State generated/posted/accepted/executed delivery status. If no handoff is required, do not manufacture one.
>
> **Closeout:** Check for remaining executable local obligations, unresolved decisions, untransferred required work, unsupported completion claims and valuable knowledge at risk of loss. Report briefly: disposition; verified work and evidence limits; execution score; top three lessons; knowledge destinations; remaining owners/blockers; complete handoff block when required; exactly one next action. End with exactly one standalone line: `Continue here`, `Decision needed`, `Hand off before archiving`, or `Ready to Archive`. A low score does not prevent archiving; an unrelated backlog does not block local closeout.

## Retrieval and usage

- **Inside this conversation or a project chat:** Say `Retrieve conversation handoff prompt.` and ask the assistant to retrieve this file from `whiterosecoffee/_BASKET`, path `orchestration/conversation_closeout/HANDOFF_PROMPT.md`, before applying it. The short phrase is not a registered automatic command.
- **When retrieval is unavailable:** Paste the full block above. Do not claim the file was fetched.
- **For reproducible offline reports:** Supply reviewed evidence JSON and run `python -m orchestration.conversation_closeout --input evidence.json --output closeout.md`. This CLI does not read ChatGPT transcripts or authenticate citations.
- **For new sessions:** State the repository and exact path; retrieve the latest version from main if integrated, otherwise from PR #170's branch. Never assume this draft exists on main.

## Maturation policy

This protocol should evolve from observed pilots and failures, not speculative feature growth. Each revision should record: concrete observed gap, smallest correction, regression fixture, evidence of improvement, owner, exact commit and compatibility impact. Keep the stable short invocation while versioning the full procedure. Review unknown theory tags against existing families before expanding taxonomy. Do not turn taxonomy gaps into automatic new issues.

### Known limitations and acceptance gates

1. Full transcript availability is not guaranteed; extraction is an assistant task.
2. Evidence JSON is supplied by a reviewer; the CLI checks structure but does not independently authenticate sources.
3. Execution-quality scoring is a judgment aid, not a productivity metric.
4. Semantic equivalence, deduplication and contradiction resolution are not yet automatic.
5. PR #170 is draft; local tests and a representative pilot have been reported, but main integration and component-specific CI acceptance must be independently confirmed.
6. Adoption into authoritative project instructions requires B00 approval; do not silently edit `AGENTS.md` or the PR #25 queue.

**Success:** An independent receiving session can recover this prompt, reconstruct the necessary objective/evidence/lessons, identify one executable next action, and avoid redoing completed work or creating a parallel framework.
