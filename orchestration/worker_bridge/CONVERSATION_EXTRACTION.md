# Reusable conversation extraction contract
Contract: basket.conversation_extraction@1 (prompt specification; no executable schema or runtime claimed).
Owner: B00 #136. Independent of the [integration contract](CONVERSATION_INTEGRATION.md).

## Copyable prompt
Analyze the supplied conversation and attachments as historical evidence. Produce a self-contained, deduplicated intelligence handoff that another worker can use without this conversation. Do not claim GitHub integration, independently authorize implementation, or certify archive readiness.

Input: conversation text or accessible source artifacts; optional source conversation ID, known GitHub references, attachment inventory and extraction cutoff. If context is incomplete, identify the missing span/artifact and its consequences. Do not infer unavailable content or fabricate source IDs, URLs or timestamps.

Output these fields in a standalone handoff:
1. Identity and provenance: source ID (null if unavailable), supplied evidence, cutoff, source locations and completeness limitations.
2. Original objectives, their evolution and current intended outcome.
3. Durable user decisions, authority boundaries and rationale; distinguish explicit decisions from assistant proposals.
4. Requirements with stable IDs and observable acceptance criteria.
5. Principles and invariants, architectural patterns, prior-art families and reasons they may apply.
6. Analytical methodologies: baselines, assumptions, units, time semantics, uncertainty, validation and falsifiers.
7. Specific use cases and representative positive/negative scenarios.
8. Evidence and provenance pointers, source excerpts when supplied, and verified facts versus issuer statements, third-party claims, inference, scenarios and unknowns.
9. Important reasoning and assumptions needed to continue; concise rationale, not redundant conversational prose.
10. Contradictions, corrections and superseded approaches, with the replacing decision and unresolved conflicts.
11. Completed versus unfinished work, with actual artifact/test evidence; reported completion is only a claim without evidence.
12. Known GitHub issues, PRs, commits, destinations and owners, explicitly unknown when not supplied.
13. Dependencies, ownership constraints, unresolved questions, next actions and one highest-priority next action.

Use explicit dispositions: retained, superseded (replacement reference), deferred (owner/return trigger), or unresolved. Preserve failures and source vintages. Deduplicate repeated discussion without deleting unique requirements. Never turn a conversation's financial claim into independently verified source evidence.

Return status ready_for_orchestrator only if every supplied durable requirement/decision has a disposition and missing evidence is explicit; otherwise incomplete with named gaps. Always return archive_ready=false: the receiving orchestrator must independently reconcile current repository evidence.

## Acceptance and failure semantics
A complete source with an objective correction retains both the old objective (superseded) and the final decision. Missing attachments produce explicit gaps, never invented excerpts. A claimed merger remains unverified until official evidence is supplied. A draft PR remains unfinished integration. Repeated requests yield one requirement with all relevant provenance. Extraction must work without GitHub access; access failure does not authorize writes or erase supplied references.

This is a reusable prompt contract, not a second capability registry. Future machine-readable qualification belongs to existing #103/PR104, not a new schema family.
