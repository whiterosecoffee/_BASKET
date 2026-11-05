# B00 v2/v3 closeout comparison — 2026-11-04 (America/Chicago)

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
