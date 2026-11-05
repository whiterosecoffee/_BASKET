# B00 v2/v3 closeout comparison — 2026-11-04 (America/Chicago)

## Repository delivery / automatic QC implementation increment

User authorized primary-work persistence, a QC intake file, automatic review and
archive, with project-wide prioritization replacing manually sequenced prompts.
Current #136 explicitly identifies Issues as authoritative and old queue.json as
historical. Therefore QC_QUEUE.json is an intake index, not another task backlog.
No planner, shared controller or workflow ownership is taken over.

Implemented qc_intake.py using existing worker-task JSON Schema plus permitted/
declared_subset helpers; safe pinned primary/handoff references, full item ID
coverage, SHA256 identity/readback, duplicate-safe append, external canonical
priority order and accepted/superseded receipt projection. It performs no network
requests, scheduling, arbitrary command execution or domain writes. Source
authenticity and semantic QC remain worker duties under QC_WORKER.md. Artifact
readback is an explicit worker step, not implied by enqueue's structural checks.

Independent reviewer ran initial 17 tests and reproduced two failures: issue URL
could disagree with number, and artifact/item reordering duplicated a request.
Two regression tests were then run and both failed. Corrections require exact
issue URL identity and normalize set-like artifact/inventory order for hashing.
All 19 tests now pass locally (zero skips). Task claims remain immutable; live
lifecycle changes are recorded on existing issues, not new intake revisions.
This does not claim authentication of arbitrary receipt URLs or exactly-once
external side effects. Concurrent metadata commits require expected-head CAS.

The complete source handoff is QC_HANDOFF.md. Primary work remains this candidate,
comparison, tests and adapter in owned versions/**. Initial queue entries pin
committed artifact bytes in a subsequent commit, avoiding self-referential SHAs.
Review archive receipts are immutable per request ID; failed/blocked/rework stays
pending and is routed to existing source issue. Review acceptance cannot close
implementation obligations or authorize merge. Initial priority is reconciled on
existing #136. Future reviews must refresh that context, not blindly follow this
snapshot or event arrival.

One GitHub PR-event automation is configured separately after publication. It
uses PR commits/comments as wake-ups for queued submissions, not unsupported
filesystem or issue-only hooks. Setup success is not proof of a future run.
No existing paused automation is resumed or repurposed. Final exact revision,
readback, automation ID and observed review evidence belong in PR179 resolution.

## Project-wide methodology assessment — subsequent user-directed review

Assessment baseline: PR179 at 1102ab9986296e662c673485897f04865c90b275. Equal-weight 0–5 rubric: 0 absent, 1 intent only, 2 partial, 3 adequate bounded design/evidence, 4 strong with gaps, 5 independently demonstrated across representative domains. Design and verified readiness are different judgments, not completion percentages, performance measurements or probabilities. Scope is this proposed project-wide method and inspected integration surfaces, not a claim to have audited every repository component. Medium confidence in design findings; low confidence in operational coverage.

| Dimension | Design /5 | Verified readiness /5 | Evidence or gap |
|---|---:|---:|---|
| Intent/knowledge conservation | 4 | 2 | Three bounded examples; full transcript generalization absent |
| Stable role/ownership | 4 | 2 | Catalog and task evaluator exist; end-to-end routing not demonstrated |
| Schema and version compatibility | 4 | 2 | Task/result schemas exist; draft component ports do not supply every domain schema |
| Repeatable recipes | 4 | 2 | Worker library contains ordered recipes; universal version binding not established |
| Domain adaptability | 3 | 1 | One long chain would over-process research; specialization newly specified |
| Evidence/acceptance discipline | 4 | 3 | Existing evaluator rejects four tested invalid evidence cases |
| Atomic ownership/concurrency | 3 | 1 | Controller README explicitly leaves multiwriter transactional leasing to B08 |
| Replay/crash recovery | 3 | 1 | Replay required; crash/side-effect reconciliation not demonstrated here |
| Semantic correctness | 3 | 1 | Shape/phrase tests cannot establish complete meaning or financial validity |
| Reuse/integration simplicity | 3 | 2 | Existing planner/controller/contracts reusable; draft branches remain fragmented |
| Cost/proportionality | 2 | 1 | Routine scorecard overhead; no measured cost or conflict reduction |
| Adoption/consumer feedback | 2 | 0 | No project-wide receiving outcomes observed |
| Total | **39/60 (65/100)** | **18/60 (30/100)** | Rounded equal-weight judgments; no uplift awarded for these new edits |

The strongest generalization is stable interfaces plus repeatable work-class recipes. It should reduce format negotiation and accidental reassignment after enforcement and adoption, but cannot eliminate legitimate conflicts caused by new requirements, incompatible versions or concurrent changes. The earlier response's fixed five-role sequence was too broad: routine research must not automatically launch implementation or CI workers. Stable roles are reusable; particular chat sessions and model instances are replaceable.

### How the same method applies elsewhere

| Work class | Existing pattern/role | Specialized contract and acceptance |
|---|---|---|
| Source/issuer research | evidence_researcher; issuer_ledger/narrative_analysis | Source class, revision/availability, competing claims, falsifiers; semantic/source review, not merely JSON validity |
| Market ingestion | B02 data_engineer; historical_replay | Entitlement, instrument/session identity, one session per physical JSONL, local coverage first, persist/readback, duplicate/correction/restart proof |
| Valuation/traversal | Domain owner; economic_traversal/economic_sensitivity | USD/unit/period alignment, missing-input behavior, deterministic arithmetic; historical validation separate from forecasts |
| Contract/schema migration | B00 contract_engineer; lossless_migration | Producer→consumer compatibility, explicit version transition, negative fixtures, retained prior data and rollback |
| Software delivery | Domain implementation; qa_reviewer/independent_ci | Scoped diff, executed unit/negative tests, exact-head independent acceptance, authorized integration and main verification |
| Deployment/monitoring | Existing B08 runtime plus domain owner | Durable transactional claims, health, restart, bounded retries, observable side effects and alerts; code presence is not operation |
| Closeout/knowledge capture | Source role→B00; current closeout infrastructure | Complete source-linked obligations/knowledge, uncertainty, recipient and usable first action; no invented follow-up work |

These are applications of existing capabilities, not new registered recipe IDs. A domain adapter supplies specialized payloads; it must not replace common task/evidence/authority contracts. Universal does not mean one giant schema: use the existing control envelope, referenced domain schemas and a checked procedure binding. Keep their versions explicit and compatible.

### Findings from current repository surfaces

Freshly read main: orchestration/planner/worker-library.json (blob 7bd751001563a3d4bd2eb6dc31d22ac244081832), WORKER_JOBS.md, orchestration/agentic/README.md and orchestration/worker_protocol.py. The library already has profiles, capabilities and eight recipes. WORKER_JOBS already defines attempt/retry lineage and prohibits invented effort claims. The agentic README already describes collision detection, evidence hashes, append-only events and local single-writer fsync, while explicitly reserving race-safe multiwriter leases for B08. Reuse them instead of a new framework.

Inspected PR104 component schema at 3908ef1dc33c65ee19e87b54a6d63a191659b9fa: it names component/owner, versioned input/output schema refs, determinism, error retryability and B01 acceptance. It remains draft; schema_ref strings alone do not validate payload compatibility. The current handoff schema uses Lnn lane IDs; worker sparks use Bnn. Require a checked mapping, not a guessed substitution.

Executed the existing worker_protocol.py with its fetched B05 task/result and 2026-10-16 historical evidence fixture. It returns component_verified_review_pending and merge_authorized=false. Four scratch mutation probes reject wrong spark, out-of-scope changed path, stale CI SHA and duplicate acceptance IDs with evidence_invalid. These are tests of supplied historical fixtures, not current B05 or whole-project readiness. First path mutation mistakenly targeted the first unrelated PR; the assertion failed. Corrected probe selects report.pr.number, then all four reject. This was a probe construction error, not a demonstrated evaluator defect. No existing code or tests were modified.

### Concrete improvements applied in this draft

1. Replaced unconditional five-role interpretation with work-class specialization; B01 is required where acceptance calls for it, not for every research note.
2. Added global invariants versus domain-specific evidence, stable role identity versus replaceable executor, and explicit not-applicable step rules.
3. Required narrative and structured outputs to preserve the same retained inventory; structural validity does not prove semantic fidelity.
4. Added crash/side-effect reconciliation, transactional claims/fencing, replay identity and explicit limits on exactly-once claims.
5. Added cache invalidation, bounded retries/resources, proportional review, migration/rollback and measured consumer-outcome criteria.

These are specification improvements only. The existing seven closeout tests are rerun for regression, not claimed to validate these runtime requirements. The prior independent review applies only to its recorded revision; this assessment is author review. No blanket operational score increase is claimed.

### Smallest integration sequence and measurable gates

| Stage | Existing owner/destination | Deliverable and gate |
|---|---|---|
| 1 — bind one existing work class | B00 #103/#106/#136 | One authoritative mapping of owner, profile, recipe revision, input/output schema versions and acceptance; resolve Bnn/Lnn mapping. Reject missing/incompatible bindings before dispatch |
| 2 — compose current validators | Existing B00 controller owner | Invoke existing task/result/schema/ownership checks at dispatch and acceptance. Same valid input selects same route; wrong receiver/version fails before mutation |
| 3 — qualify shared writes | Existing B08 #34 with B00 controller | Transactional claim and fencing, crash-after-write recovery; two conflicting writers cannot both commit. Read-only pilot can proceed without this write capability |
| 4 — pilot across unlike work | Existing closeout owner plus one existing data/compute owner | Source-linked closeout replay and one frozen data/compute replay; no new workers just to satisfy a matrix. Consumer reads outputs without reconstructing source conversation |
| 5 — independent acceptance | Existing B01 acceptance owner (#105 for component contracts), B00 semantic review | Negative binding/version/replay/concurrency tests actually execute; independent semantic annotations and exact-head evidence retained |
| 6 — expand only on evidence | B00 existing controller/planner | Record baseline and candidate first-pass acceptance, duplicate effects, unauthorized writes, lost obligations and conflict escalations per comparable task. Track actual tokens/tool calls when available; no invented savings |

Cost discipline: reuse existing validators and profiles; start with one mapping and one consumer, not a repository-wide retrofit. Exact effort/token cost is unknown. Main benefit to test is fewer repeated negotiations and failed handoffs without lower evidence quality; main cost is added contract maintenance and validation. Stop expansion if review overhead increases without measured benefit or if valid domain work is blocked by an overgeneralized schema.

One next existing-owner action: B00 #103/#136 bind the closeout work class to current schemas/recipe and controller checks; #179 supplies requirements and evidence only. Existing ownership prevents silently modifying those controller/contract paths from this versions/** draft. No merge, deployment, new registry, queue or automatic policy adoption is authorized by this assessment.

## Decision

Keep v3 a candidate. Its mandatory B00 block addresses the recipient-loss requirement by contract, but three deliberately small paired manual cases cannot prove reliable extraction from full conversations. Both versions preserve the annotated substantive knowledge in these cases. Do not claim a measured retention improvement or promote policy from a passing test suite.

User explicitly requested continuation inside the appropriate existing draft PR: #178 / #179, branch work/178-module-contract-reconciliation. All writes remain versions/**. Current-main governance, B00 catalog and worker protocol were read. The 61 returned open PRs' complete changed-file lists were checked, including 294 paths on PR147: only PR179 writes versions/**. Relevant issue scopes #169/#178/#184 were reconciled; #184 archives separately and does not own this subtree. No active-worker count is inferred. PR170 parent-module ownership remains read-only.

## Frozen evidence

- V2 source: PR170 at 06a7f0a1b197400f48b0317529c4184d48efe142; Git blob f3e6c4b8a656b27feeed4ea32b86792faa1a7be2. Full preserved source is adjacent.
- Unamended v3: PR179 at e949f402b84471dca89ba78f2a442573b0c8db39; candidate blob df167a1a25a90a5ff427bdbb4ca0efda6eb8b3e7. Recoverable from Git history; no duplicate snapshot introduced.
- Existing supplied-evidence corpus: PR170 pilot.json, blob b39d2954f204cac0a01bf71ee9de7401bb233b71. Routine, research and reconstructed repository cases. Its historical source is issue169 comment6621962657; original pilot JSON/full transcript unavailable. It must not be called a full-conversation reproduction.
- Saved actual handoff: research/composites/macro_delta_handoff/HANDOFF.md at 83553bc170a83bfea77349554db9cc9f67cefafe (PR159). Source reports intake acceptance, D1-D8 still 0/8 fully accepted, timestamp/no_new_observation defect and manifest/payload distinction. This review inspected the artifact, not its underlying test logs or payload.
- Reused acceptance ideas: PR177 PROMPT_EVALUATION.md at af841f3e7b7522f41839407720e54bf1e896b3d3, blob 028ac7b90b5e457b43669a1923a56b5fd56f7673. Repeated review, quoted authority, deferred triggers, missing transcripts and source-anchor loss checks already exist as proposed cases. No competing evaluation service is warranted.

## Comparison

| Requirement | V2 | Original v3 | Finding/action |
|---|---|---|---|
| Required B00 recipient | Functional owner; handoff conditional | One B00 block even after local completion | Intentional incompatibility; test routine completion explicitly |
| Material knowledge | Causal knowledge units, no arbitrary truncation | Inventory first, stable IDs, loss audit | Both retained four concrete research mechanisms; no demonstrated semantic superiority |
| Ownership | Existing owner/branch, forbidden writes | Adds inherited NEXT vs assignment distinction | Test quoted NEXT, optional cleanup and forbidden B01 writes |
| Evidence | Exact-head checks, source classes, CLI caveat | Source/revision and self-audit limits | Historical report cannot become current CI proof; test explicit mutation |
| Unresolved commitments | Obligation ledger | Explicit completion/transfer/block/drop; deferred triggers | Preserve source acceptance vs implementation acceptance and unanswered question |
| Executable handoff | Exact commands and dependency sequence explicit | Acceptance/next action, less explicit ordered steps | Restore known commands and prerequisite order; unknown commands stay unknown |
| Retrieval/default | Exact path/branch and CLI limitations | Invocation alone could imply changed default | Add candidate retrieval path/ref and unchanged v2/default/CLI boundary |
| No duplicate work | Reuse existing destination | No duplicate issues/branches/queues | Repeated-review amendment keeps full block while reporting no material delta |
| Retrospective | Can remain outside copied block | Must remain inside block | Intentional stronger output requirement; tests move anchors outside block |
| Routine burden | No manufactured handoff | Broad scorecard still required | Known verbosity cost; no measured benefit or effort claim |

V2 taxonomy examples, ranking weights and archive terminal vocabulary are not copied into v3. Their absence is not automatically a regression: tags/rankings are optional aids and terminal behavior intentionally changes. Existing worker contracts remain authoritative; candidate amendments make that explicit. No CLI migration or schema equivalence is implied.

## Tests and interpretation

`acceptance_cases.json` contains source text, expected propositions, paired outputs and assessments. Two synthetic cases were manually authored by a separate reviewer applying the unamended prompts; the third is a root-authored bounded saved-artifact case with explicitly synthetic authority/cleanup/repetition stressors. The macro case excludes original market/physical-supply objectives and detailed D1-D8 specifications; it tests only the declared excerpt, not full artifact completeness. These are review samples, not independent random samples, automated model invocations or historical transcript replay. Scores inside examples assess their fictional work attempts, not this project or protocol effectiveness.

The independent reviewer inspected both source protocols before amendments, reran the existing 23 tests and all three existing supplied-evidence cases, checked the v2 blob, and reviewed candidate changes and tests. This is independent delegated review within the same agent session, not B01 acceptance, a blind external audit or downstream consumer adoption.

Commands actually run on connector-fetched local files:

```
python -m unittest orchestration.conversation_closeout.test_closeout -q
python -m unittest discover -s orchestration/conversation_closeout/versions -p 'test_*.py' -v
```

Results: existing 23 tests pass; seven new tests pass. New tests include 33 missing-anchor subcases, 11 forbidden-addition subcases, three wrong-recipient and three duplicated-block subcases. Exact source-byte check protects v2. Existing routine replay produces Ready to Archive with no handoff; research/repository retain four supplied insights. This confirms the unchanged CLI is not a v3 execution engine.

The test-only oracle checks exact anchors INSIDE one copied block. It rejects seeded omissions and specified unsafe assertions; it cannot authenticate evidence, recognize arbitrary paraphrases, detect every contradiction or prove semantic completeness. Positive anchors plus contradictory wording can still fool it if not represented in forbidden vectors. Manual proposition review remains necessary. No new runtime API or schema is introduced.

Observed corrective attempts: local source reconstruction initially added a trailing newline; byte comparison caught it, exact fetched bytes were restored before acceptance. Initial recipient check allowed only Receiver: B00; independent review identified valid To: B00 / To B00 outputs and the check now accepts all three. Repeated-review amendment initially risked reference-only output; reviewer required full-block essentials and that correction is applied. No claim of earlier red-suite execution is made for these review-detected defects.

## Remaining gates and complete B00 handoff

````text
Receiver: B00, existing issue178 / draft PR179, whiterosecoffee/_BASKET.
Mode: review of candidate validation; no merge, release, default switch or new worker authorized.
Scope: versions/** only; PR170 CLI/default and B01 workflows remain untouched. Source v2 blob f3e6c4b8a656b27feeed4ea32b86792faa1a7be2 is immutable. Latest checked heads and post-publication verification belong in the PR resolution, not a fabricated self-referential commit field.
Completed: v2/v3 requirement comparison, saved-handoff inspection, three bounded paired manual cases, seven negative/preservation tests, original 23-test replay, independent delegated review, compatibility and actionability amendments. Reuse these artifacts and PR170; do not recreate tests, queues, schemas or issues.
Knowledge: a formatter preserves supplied fields but cannot prove source extraction; artifact retention and semantic completeness need separate evidence. Current-head binding prevents stale CI promotion. Stable source-linked knowledge units preserve rationale and falsifiers across compression. Review must distinguish source intake from implementation acceptance and unknown evidence from failure. Exact phrase checks are mutation regressions, not a semantic judge.
Unresolved: generalized extraction reliability, held-out full-conversation coverage and downstream B00 actionability are not established. Original historical transcripts remain unavailable. Mandatory routine scorecard has a verbosity cost; benefit unmeasured. Shared CI is not claimed to run the new subtree tests. No policy adoption or CLI migration performed.
Sequence: fetch current PR179 head and changed paths; run the versions unittest command above against that exact head, checking v2 bytes and all seven named tests. Inspect independent review evidence and compare manual propositions with both outputs. Before policy promotion, use held-out authorized complete conversations, freeze annotations before generation, apply both exact prompt revisions, retain raw outputs and disagreements, and independently verify false-authority rate, lost requirements/mechanisms and receiver actionability. Do not create a new system for that trial. If transcripts are unavailable, retain an explicit limitation rather than synthesize history. Existing PR170 remains a separate integration decision.
Acceptance: current-head tests/readback and independent review support this bounded draft validation; broader adoption additionally requires held-out/receiving evidence and explicit authorization. Retirement: record disposition of this validation in existing #178/#179, leaving promotion gates explicit.
One next B00 action: review the exact published candidate head and bounded evidence in PR179 for disposition; do not infer approval to merge.
Transfer state: this handoff is persisted with the validation; receipt, acceptance and execution by B00 are unknown.
````
