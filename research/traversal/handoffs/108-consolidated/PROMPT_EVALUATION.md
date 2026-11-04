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


## Deeper evolution: authority, loss-audit independence and adopted learning

The next revision is at prompt commit `c4d2f5125d91cf863c9ff0d63355dafa70adf354`. This is a design evolution, not a measured score improvement. Baseline design score68/100 and retrospective conversation score70/100 remain unchanged and refer to different objects.

### Five deeper failure modes and behavioral changes

| Failure mode | Why the prior procedure was insufficient | New requirement / falsifiable check |
|---|---|---|
| Correlated extraction/audit omissions | The same reviewer can omit an idea and then approve a summary that also omits it | Separate source-anchor loss scan, particularly around pivots and interrupted requests; label self-audit, not independent verification |
| Authority drift | A retrieved historical directive, assistant suggestion or promise can become an unintended implementation instruction | Track source class and authorization; explicit earlier user instructions remain obligations unless evidence resolves them, while opportunities remain proposals |
| Deferred-work burial | A retained “later” idea can be technically recorded but practically undiscoverable | Preserve destination, why it matters and reconsideration condition; distinguish defer from reject/discard |
| Recovery without evolution | Prior capture emphasized existing statements but could miss useful new applications | Separate third track for NEW INFERENCE/PROPOSAL with premises, expected value and falsifier; never attribute synthesis to the user |
| Learning without adoption | A lesson in a comment can remain disconnected from tests, contracts and consumer outcomes | Track capture→owner decision→implementation→verification→consumer result; no benefit or score claim from longer text |

The revision also distinguishes execution/retention/transfer/scope as separate dimensions without imposing a replacement project schema. Acknowledgment is not adoption; source closure is not feature completion.

### Actual-source manual checks

These are reviewer applications to this available conversation, not independent model trials.

1. Early user instruction “Don't do this new task yourself. Just delegate it.” must survive later “execute all unblocked work” language as an authority constraint on the affected work. The original historical task and delegated reusable engine are separate. A successful review cannot simply reopen another owner's implementation.
2. Later CRWV/ORCL first-milestone choice narrows the next receiving action but does not delete nested ranges, directional effort, historical matching or useful context interfaces. Those remain requirements/research/optional extensions according to their original authority.
3. The user's instruction that the prompt derive identity and mission applies to the reusable input procedure. Generated handoffs should still contain discovered concrete scope/receiver details. Removing all concrete context from generated output would be an incorrect generalization.
4. The old request to archive after orchestrator acceptance was subsequently changed to user-pasted transfer preparation as the source endpoint. Preserve both and their temporal relationship; do not claim receiver execution merely because local archive is permitted.
5. The70/100 source execution score and68/100 prompt design score concern different objects. Rewriting the prompt does not retroactively improve either score.
6. The source's static range_start concern was superseded by verified source behavior. Preserve why the concern existed, retire the duplicate fix, and retain caller-horizon acceptance as a different open issue.

Each checked interpretation has a destination in the prior #108 packet/review and this prompt proposal. This small chosen sample does not establish complete source recovery or generalization.

### Owner pilot: metamorphic cases to expose semantic failures

Reuse #169's existing evaluation surface; do not create another service. Freeze a source/annotation revision and expected meaningful changes before running trials.

- Append an unrelated final task: earlier uncanceled obligations and valuable ideas should remain represented.
- Append an explicit cancellation: only the affected obligation changes, with cancellation lineage retained.
- Replace “must implement” with “could research”: the retained concept may be unchanged, but execution authority must differ.
- Paraphrase or duplicate an idea: meaning and source lineage survive, without duplicate implementation tasks.
- Remove the original transcript and provide only a summary: coverage/authority confidence decreases; absent details are not invented.
- Add a falsifying observation or revised source: hypothesis and claim state change with lineage; old evidence is not silently rewritten.
- Redact a sensitive identifier: useful mechanism survives without leaking the identifier into repository artifacts.
- Repeat identical review input with unchanged evidence: no new issue, duplicated artifact or unexplained score increase.

These cases are SPECIFIED, NOT EXECUTED independent behavioral tests. Candidate metrics: missed annotated explicit instructions, retained mechanism/condition coverage, false-authority promotion, contradiction resolution, recovered opportunities, receiver clarification burden, unnecessary work and privacy exposure. Use defined denominators only; annotator disagreements and unavailable context remain explicit. Source-grounded independent review and held-out receiving trials are still needed.

### Effort and complexity

The full procedure is longer than its predecessor; greater length is a cost, not evidence of improvement. Keep routine outputs compact, reuse existing records, avoid external retrieval that cannot affect decisions, and test whether the added requirements reduce actual loss without increasing false obligations or coordination. No measured token/cost savings or efficiency improvement is claimed.

### Next owner action

#169 owner evaluate these authority/loss cases against the previous and candidate procedures on the same frozen annotated inputs, using an independent review where available; accept only the behavioral deltas supported by evidence. Preserve earlier good behavior and report regressions. This is a bounded evolution of the existing protocol, not a new framework or authorization to reopen unrelated project work.
