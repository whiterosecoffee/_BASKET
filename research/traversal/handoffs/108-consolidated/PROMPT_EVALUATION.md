# Conversation recovery prompt — design review and retention pilot

## Purpose and evidence boundary

The user clarified that this tool must recover valuable instructions, next steps and reasoning displaced as conversations narrow to a specific deliverable. That is broader than local closeout.

This evaluation compares the previous committed prompt at `8e5aba2981bed8af425bc68acc098e2096a37697` against the revised prompt at `acd5adb3fe1379a5c54b9dd07fdc720e7be7884f`. It is a reviewer design assessment and bounded manual application to available source conversation excerpts. No independent-model comparison, production trial or measured before/after retention rate is claimed. The prior conversation execution score70/100 is a different assessment.

## Broad baseline rubric

Each dimension is out of10; equal weights. Evidence is the previous prompt's written requirements, not assumed model behavior.

| Dimension | Score | Reason |
|---|---:|---|
| Context and current objective | 8 | Explicit context inference and scope, with available-transcript limitations. |
| Recovery of displaced or unfinished scope | 5 | Original/latest objectives were requested, but there was no mandatory recovery pass for the trajectory and displaced seeds. |
| Accounting for instructions and commitments | 6 | Obligation ledger existed; every earlier instruction/commitment did not require source-linked accounting. |
| Mechanisms, reasoning and counterexamples | 8 | Knowledge units retained mechanism, limitations, alternatives and falsifiers. |
| Evidence and claim discipline | 9 | Strong source-revision, test and readiness distinctions. |
| Ownership and bounded execution | 8 | Explicit scope and external-owner gates. |
| Reuse and actionable receiving work | 8 | Existing surfaces, probes and lowest-complexity improvements requested. |
| Self-contained handoff | 8 | Complete copy block required for material external corrections. |
| Explicit loss-detection and retention tests | 3 | No explicit source-to-destination loss audit or candidate disposition check. |
| Feedback, adoption and evolutionary learning | 5 | Workflow/pilot improvements present; future-value recovery and adoption feedback were less explicit. |
| Total | **68/100** | Judgment, not completion or empirical effectiveness. |

## Design corrections

1. Two equal tracks: complete current authorized work AND recover valuable displaced scope. Do not treat one as proof of the other.
2. Inventory before highlights: explicit instructions, promises, ideas, algorithms, interfaces, hypotheses, evidence, alternatives and lessons, including unfinished fragments.
3. Separate obligations from opportunities: preservation is not execution authority; ambiguous earlier instructions cannot silently become optional.
4. Source-linked dispositions: retained/consolidated/transferred/blocked/deferred/rejected/superseded/duplicate with reasons and destination.
5. Explicit loss audit: compare inventory with output, preserving causal logic, boundaries and source lineage; repair material omissions.
6. Evolution by adoption/evidence: scored shortfalls get action/probe/owner/acceptance or justified defer, and repeated reviews report only deltas.

## Bounded manual application to this actual conversation

The following12items are a declared audit sample, not an exhaustive semantic ground truth for unavailable original/other-chat transcripts. Applying the new procedure recovered a disposition for all12. This does not prove the older prompt would omit them or that the new prompt generalizes.

| Source requirement/fragment | Recovered meaning | Disposition/destination |
|---|---|---|
| Historical CRWV JSONL replay | Original historical deliverable must remain distinct from a later engine | Historical lineage preserved in #108 packet and PR69; no new replay claimed |
| “Don't do this new task yourself. Just delegate it.” | Historical completion and reusable-tool delegation were different instructions | Preserve authorization history; feature transfer remains #108/#95 |
| One tool for any ticker with local state | Generic interface, durable observations, frozen ranges and restart | Existing #108/#95, not a competing engine |
| Read live tape without waiting for instructions | Operational ingestion request was real but unproven | External #97; bounded replay is not proof of monitoring |
| Narrow bands and $:volume | Movement effort, contacts and retained progress must survive summarization | #108 requirements and #144 research |
| Range within a range | Simultaneous intraday/swing/regime coordinates, not one sequential ladder | #108/#149/#144 |
| Check other conversations | Recover related ORCL, macro and historical-state contributions | Preserved prior retrieval; #101/#154 interfaces, not mandatory expansions of M1 |
| Verified CRWV/ORCL replay first | First receiving milestone and isolated state on shared code | #108 M1; independent proof pending |
| Consolidation handoff, accepted transfer endpoint | Source archive can coexist with externally incomplete feature | #108 accepted intake and #136; no feature-complete claim |
| One prompt in chat and pushed to repo | A comment was insufficient; actual committed file and identical copy required | PR177 source text and verified readback |
| No hardcoded conversation ID/mission | Reusable procedure derives context; generated handoff contains actual context | New prompt opening and phases1/9 |
| Score broadly; prevent shard losses | Review must recover unexecuted intellectual/requirements value, not just finish a fix | New dual-track inventory, dispositions and loss audit; #169 owner review |

## Regression/pilot cases for the existing #169 owner

Use existing harness/fixtures rather than a second evaluator. Expected behavior:
- Explicit early instruction followed by narrowed deliverable: retain unresolved instruction or source-backed cancellation.
- Rejected approach later mentioned again: retain rejection rationale; do not execute it.
- Unapproved but valuable hypothesis: preserve mechanism/destination/trigger without implementation.
- Several convergent ideas: deduplicate shared core while retaining meaningful differences and source anchors.
- Missing transcript or owner access: record unknown coverage, not fabricated cancellation/completion.
- Already accepted source transfer with external defect: complete corrective block while distinguishing source archive from feature acceptance.
- Repeated unchanged invocation: no duplicate artifacts/tasks or invented maturation.
- Before/after correction: retain original retrospective score and report separate observed improvement evidence.

These are specified acceptance cases, NOT independently executed model/harness results. The manual12-item sample is only an initial source-coverage check. More reliable evaluation requires held-out conversation shards, annotated recovery targets, independent review of retained meaning/authorization, false-obligation rate and receiving actionability.

## Remaining acceptance and adoption

The revised prompt is committed/readback-verified on PR177. No new production code, canonical data, schema or workflow. No adoption into #169/PR170 or main policy is claimed. No measured token savings or response-loop reduction.

One next action: #169 owner compare this delta with the existing full protocol and evaluate the cases using its current pilots before adoption. Keep the original traversal implementation/canonical-data work in #108/#148/#152 separate; do not revive source implementation ownership to improve this prompt's score.
