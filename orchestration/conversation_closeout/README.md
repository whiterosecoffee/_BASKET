# Conversation closeout audit — B00 draft

**Canonical on-demand conversation instruction:** [HANDOFF_PROMPT.md](HANDOFF_PROMPT.md). Retrieve this file by path from the repository before running a conversation closeout; it is the evolving full prompt. Short invocation: **apply handoff prompt**. The full v2 protocol controls the review; the CLI is a narrower supporting evaluator.

**Command:** `python -m orchestration.conversation_closeout --input closeout.json --output closeout.md`

This is a deterministic **offline report formatter and evidence-gate**, not a conversation scraper, agent, scheduler, GitHub updater, or proof of worker execution. A conversation assistant first reviews its accessible transcript and current relevant evidence, then supplies a JSON assessment. Do not pass private account records, credentials or sensitive financial data. The CLI does not verify external citations or GitHub CI.

## Input contract

JSON object:
- `objective`: nonempty functional objective.
- `local_required_remaining`, `decision_required`, `external_required_remaining`: required booleans, based on independently reviewed evidence.
- `evidence`: short source/commit/CI summary with explicit freshness and unknowns.
- `scores`: optional keys `objective_control`, `execution_conversion`, `reuse`, `ownership_integrity`, `verification_integrity`, `dependency_handling`, `resource_efficiency`, `knowledge_extraction`, `handoff_quality`, `closure_discipline`; integer 0–5 or null for unobserved. Normalized only across observed dimensions. Never treat this as measured productivity.
- `insights`: optional array of `{principle, disposition, priority}`; disposition one of `already_incorporated`, `consolidated`, `transfer`, `propose`, `defer`, `discard`; priority 0–25 is heuristic.
- `handoff`: required only when external required work remains and no executable local work or decision gate takes precedence. Fields: `owner`, `destination`, `objective`, `completed`, `remaining`, `write_paths`, `prohibited`, `validation`, `next_action`. The generated prompt is always included when the disposition is transfer, even when a GitHub handoff already exists.

## Output contract

Markdown containing completion disposition, optional evidence-weighted quality score, a top-three lesson overview plus all additional supplied material knowledge, and (when required) a complete copyable handoff. Final line is exactly one of: `Continue here`, `Decision needed`, `Hand off before archiving`, `Ready to Archive`.

**Disposition precedence:** executable local obligation → unresolved nontransferable decision → external obligation requiring handoff → archive-ready. Never infer a claim from an absent field. External backlog alone is not a local obligation.

## Example

```json
{
  "objective": "Retire a scoped component research conversation",
  "local_required_remaining": false,
  "decision_required": false,
  "external_required_remaining": true,
  "evidence": "PR #104 is draft; head and CI must be refreshed by receiving owner.",
  "scores": {"objective_control": 4, "execution_conversion": 3, "verification_integrity": null},
  "insights": [{"principle": "Independent domain tests must execute, not merely appear in a passing aggregate workflow", "disposition": "transfer", "priority": 23}],
  "handoff": {
    "owner": "B00 architecture",
    "destination": "Existing Issue #103",
    "objective": "Finalize versioned black-box input/output contracts",
    "completed": "Draft manifest and architecture specification",
    "remaining": "Executable request/response schemas and independent acceptance",
    "write_paths": "Only authorized B00 schema and architecture paths",
    "prohibited": "No B01 workflow or B02 data writes",
    "validation": "Run schema negative fixtures and exact-head CI; preserve failures",
    "next_action": "Review current PR #104 and reconcile approved interface"
  }
}
```

## Tests

`python -m unittest orchestration.conversation_closeout.test_closeout -v`

## How to invoke in a ChatGPT conversation

Say: **apply handoff prompt**. Retrieve and follow `HANDOFF_PROMPT.md`; do not substitute the CLI's narrower evidence contract for the complete analysis.

If ChatGPT cannot execute the repo command, it can still perform the review in-chat and produce the same evidence JSON. Do not claim a CLI run occurred.

## Orchestrator integration

The existing project CLI delegates directly to this module:
`python -m orchestration.agentic.cli closeout --input evidence.json --output closeout.md`.
Use `closeout --help` for options. No installed `basket` executable or automatic
routing for `apply handoff prompt` is claimed. Delegation bypasses controller
state and GitHub collection. Existing worker task/resolution contracts remain
authoritative; no second scheduler or queue is introduced.

## Evidence and knowledge extension (draft)

Optional `claims` is an array of objects with `id`, `type`, `text`, and for `repository_verified` or `independent_test`, mandatory `source_ref` and `revision`. Types: `user_assertion`, `conversation_observation`, `repository_verified`, `independent_test`, `inference`, `proposal`, `unknown`. The CLI validates the presence of references but **does not fetch or authenticate them**.

Each insight may additionally contain `pattern`, `methodology`, `application`, `evidence`, `limitations`, `architecture`, `capability_match`, `rationale` and `claim_ids`. The report preserves these details and includes all supplied material insights and claim provenance in transfer prompts. A referenced claim ID must exist in the supplied claim array. An evidence string alone does not constitute independent verification.

The tool still requires an assistant to interpret the conversation and supply the structured input. It does not perform semantic deduplication, transcript extraction, contradiction resolution, or live GitHub verification. Those remain proposed capabilities, not acceptance claims.

## Prior-art and methodology cohesion

For **material architectural or methodological insights**, supply concise `prior_art` pointers. This is a recommended review discipline, not a forced citation for routine observations. Each pointer has four required strings:

- `family`: established family (for example, Design by Contract, event sourcing, hexagonal architecture, CQRS, reproducible builds, scientific falsification, or postmortem learning).
- `mechanism`: the specific reusable mechanism, not just the family label.
- `applicability`: which component or workflow benefits.
- `boundary`: when the analogy does not apply or what it does **not** establish.
- Optional `reference`: an existing project artifact or trustworthy external reference; absence must not be disguised as verified research.

Example: `"prior_art":[{"family":"Design by Contract","mechanism":"typed input/output ports","applicability":"B10 valuation engine","boundary":"schema validity does not establish financial correctness","reference":"architecture/BLACK_BOX_COMPONENT_CONTRACT.md"}]`.

The report and transfer prompt retain these pointers. Prefer one or two meaningful families per insight, not a taxonomy dump. An LLM-supplied family is a design analogy, not independently verified prior art. The CLI validates structure only and does not fetch references or establish conceptual equivalence. Do not invent a family to satisfy a form.

## Controlled theory tags

Substantive architectural insights marked `"architectural": true` should identify all applicable `theory_tags` without an arbitrary maximum. Tags are optional for routine lessons; provided tags must be unique and nonblank; unknown or missing architectural classifications become explicit taxonomy-review gaps, not silently discarded or automatically adopted. Current internal vocabulary: `DBC` Design by Contract; `HEX` ports/adapters; `DAG` dependencies; `EVS` event sourcing; `CQRS` read/write separation; `IDEM` idempotency; `PIT` point-in-time; `PROV` provenance; `FALS` falsification; `REPRO` reproducibility; `FSM` state machines; `POST` postmortems; `INFO` compression; `DEC` decision theory; `MOD` modularity; `OBS` observability.

Example: `{"principle":"Versioned black-box ports","architectural":true,"theory_tags":["DBC","HEX","MOD"],"disposition":"transfer"}`. Report and handoff retain the tags. The classification is a concise methodology pointer, not a citation or proof of correctness. Avoid invented tags or forced analogies. B00 must approve vocabulary evolution; do not create a parallel taxonomy registry.

## Taxonomy maturity policy

No maximum tag count. The internal dictionary is a known-vocabulary starting point, **not** an exhaustive ontology. An unknown tag or missing classification on an architectural insight is retained as a `taxonomy_gaps` finding in the evaluated result, report, and handoff. It signals B00 review of existing theory families, naming and applicability; it does not authorize automatic canonical expansion, duplicate issues or another registry. Review should first map to an existing family, then propose a new family only if genuinely distinct. Unknown classifications are not proof of invalid architecture, and no claimed taxonomy coverage should be inferred from an empty list of tags. Duplicate or blank tags still fail input validation.


## Retention pilot and invocation verification (2026-11-04)

B00 continuation of #169 / #170. The durable authoritative **draft prompt for this
workstream** is HANDOFF_PROMPT.md, not this formatter. Invocation stays exactly
`apply handoff prompt`. This is a natural-language request to retrieve and apply
that file, not an automatically registered software command. Read from
`work/169-conversation-closeout-cli` until integration; after integration retrieve
`orchestration/conversation_closeout/HANDOFF_PROMPT.md` from current main. Branch
retrieval succeeded at `53fb357ef119fca7634f453a41da9dd511dfb47f`; main returned 404.
After merge, verify retrieval on main before claiming availability. The same workstream subsequently added Python CLI delegation at
`c3743df5fc0c1ceb9dc953aa0c24fa07d7c50f68`; it is preserved by this finalization.
That executable interface does not register the natural-language phrase.

### Sources and comparison method

The existing pilot is recorded in #169 comment `6621962657` at
`64d0ce69ab3be4d28e07aef886417c2795553341`. Its original JSON and full transcript
were not committed and are unavailable in the supplied context. Its reported
68/100 execution score is not a knowledge-retention measurement. We reconstructed
its three material units from that comment and later corrections, adding the
current invocation obligation as a fourth material unit. `pilot.json` contains
that repository replay plus explicitly synthetic routine and research boundary
cases. These are supplied-evidence preservation checks, not independent real-world
conversation samples or proof of automatic semantic extraction.

Read v1 from `377b6b41191846ece69ed9a1e39c4e9ac73f8257` and v2 from `53fb357e…`.
Both prompts already request substantive knowledge; v1 must not be scored as losing
knowledge merely because v2 is longer. Apply both to the same recovered evidence:

| Knowledge | v1 procedure / available earlier pilot | v2 review and repaired formatter |
| --- | --- | --- |
| Objective and evolving requirements | v1 requests latest controlling objective; earlier pilot predates exact invocation | Preserve original offline-tool objective and latest causal-transfer/invocation requirements in objective and copyable block |
| Completed and unfinished work | Both distinguish verified/unverified; historical pilot points to #169 | Reuse evaluator and discovery bridge; refresh head and acceptance before review; do not rebuild |
| Principles and theory families | Earlier pilot preserves three principles and family tags | Preserve those mechanisms and pointers, with fourth invocation obligation; no taxonomy expansion |
| Patterns and mechanisms | v1 requests them; formatter loses pattern in copyable block | Copy supplied pattern with its principle |
| Ordered methodology | Earlier pilot repair retained method; v1 requests dependency order | Preserve refresh -> tests -> actual CI log -> retention -> integration review |
| Architecture and ownership | v1 requests boundaries; formatter omits architecture | Copy reviewer JSON -> formatter -> B00 receiver, B01 workflow ownership and forbidden paths |
| Concrete applications | Existing pilot repair already retains application | Preserve application; prior-art applicability now also survives copy |
| Evidence, falsifiers, limits | v1 requests these; formatter leaves claims outside copyable block | Copy evidence, claim class/source/revision and boundary; historical claims stay historical |
| Decisions and rejected alternatives | Both request rationale; formatter copies rationale only for first three | Preserve supplied choice/rejection/reconsideration rationale for every material unit |
| Existing destinations and acceptance | v1 names existing destination; formatter loses per-insight capability match | Copy existing artifact/owner destinations, scope, ordered next action and acceptance |

Observed **loss** in the pre-repair formatter: fourth insight silently absent from
both report and handoff; pattern, evidence, architecture, capability destination,
claim provenance and prior-art applicability/reference absent from the standalone
handoff. **Distortion risk:** missing claim class/revision can make a historical
assertion look current; no factual inversion was observed. **Improvement:** those
supplied values now survive without inventing new facts, fields, taxonomy or
workflow. V2 adds an explicit knowledge-unit and obligation-ledger discipline;
this improves review actionability, not automatic extraction. Decisions/falsifiers
use existing rationale/limitations strings; no new schema is needed.

Executed replay: routine retains 1/1 principles before and after, with no
manufactured handoff; research and repository each retain 3/4 before, 4/4 after.
For each transfer case the first insight's pattern/evidence/architecture/destination
are missing before, none missing after. Regression checks every supplied material
text field, prior-art pointer, tag, claim and handoff obligation **inside the copied
block**. All three CLI outputs replay byte-identically. A receiving owner can find
what to reuse, why, prohibited changes, existing destination and first executable
check without needing the surrounding report. This proves preservation of supplied
knowledge; it cannot prove the reviewer extracted every material transcript fact.

### Regression and compatibility

`python -m unittest orchestration.conversation_closeout.test_closeout -v` runs 23
tests (including three pilot subcases). The unchanged discovery bridge imports the
same TestCase into existing orchestration CI. No B01 workflow changes are needed.
The pre-repair exact-head Actions run `41770007392`, worker-qc job `126377274428`,
names all 22 original tests within 191 passing orchestration tests; 29 integration
tests also passed. Final-head CI evidence belongs in the existing issue/PR resolution.
Local testing uses connector-fetched files because git clone failed to reach the
workspace proxy; it is not claimed as a full repository checkout.

Inputs and disposition precedence remain compatible. The first three lessons stay
in the overview; additional supplied insights appear under retained knowledge and
all are copied into transfer prompts. Callers must supply only material insights;
the formatter cannot decide semantic importance. Output text intentionally changes.
Unknown fields remain outside the supported input contract. No automatic source
authentication, contradiction resolution, registered phrase routing, merge, or
main-policy promotion is claimed. Independent full-conversation pilots and B00
policy approval remain prerequisites for promotion beyond this draft workstream.


## Review resolution and remaining adoption gate — 2026-11-19

This dated B00 review continues #169/#170. It does not adopt policy or replace
the default prompt. The interrupted 2026-11-13 write published no reconciliation;
the branch remained at `06a7f0a1b197400f48b0317529c4184d48efe142`.
The current increment changes only this README. A fresh changed-path inventory
of all 81 other open PRs found no collision with this file. Open PRs do not
establish worker activity.

### Blocker dispositions

| Concern | Checked evidence and disposition |
| --- | --- |
| Original component verification | Existing exact-SHA run [41770913789](https://github.com/whiterosecoffee/_BASKET/actions/runs/41770913789) executed 23 closeout + 5 CLI tests inside 197 orchestration tests, plus 29 integration tests. Historical acceptance remains pinned to `06a7f0a1…`; the new documentation head needs its own CI. |
| Candidate was only in chat | Resolved for the preserved v3: PR179 head `0a020f22cf9b6bcf756fe7a439cd6ffe875bcc44` stores the full candidate and exact v2 baseline. Do not duplicate or overwrite its owned versions/** files. The latest chat amendments below remain proposed. |
| Versions tests absent from mandatory CI | Resolved: [42945000165](https://github.com/whiterosecoffee/_BASKET/actions/runs/42945000165), [worker-qc](https://github.com/whiterosecoffee/_BASKET/actions/runs/42945000165/job/130275562393), names 9 AcceptanceTests + 19 QcIntakeTests + 13 QcSubmitTests at `0a020f22…`, within 283 orchestration tests; 113 integration tests pass. This is not semantic completeness evidence. |
| Default and candidate conflict | Intentional, now explicit: v2 remains default; v3 is a separate trial. Mandatory B00 delivery and the proposed closing rule are behavioral changes. The Python formatter retains its documented conditional handoff/output contract. |
| Broader semantic validation | Bounded manual comparisons and frozen-output checks exist. Independent generalized extraction/consumer effectiveness is not established. This limits broader promotion; it does not erase existing bounded test results. |
| Layered-intent and continuation work | New #169 intake comments and PR264 describe separate work, including partial-supersession gaps. They are not regressions against PR170's documented supplied-evidence formatter, and are not pulled into this finalization. |
| Main availability and integration | The branch prompt is retrievable. No merge/adoption is claimed; verify main retrieval after separately authorized integration. |
| Permission | The user's scoped finalization, documentation and existing issue/PR reporting grants cover this reconciliation. They are not blanket implementation, default-adoption, merge, release or worker-launch permission. |

Preserved candidate:
[complete v3 at checked PR179 head](https://github.com/whiterosecoffee/_BASKET/blob/0a020f22cf9b6bcf756fe7a439cd6ffe875bcc44/orchestration/conversation_closeout/versions/HANDOFF_PROMPT.v3-candidate.md).
Its current blob is `175a85b93fb64c9a736cb9174c9da40c473f21ef`.
It already distinguishes procedure from generated handoff and documents separately
authorized repo_queue delivery. Do not remove that authority or require manual
copying where repository delivery was explicitly granted.

### Exact remaining proposed amendments — prepared, not adopted

These narrow additions preserve the complete candidate rather than replacing its
knowledge extraction with a checklist. An authorized adoption change must render
one complete controlling prompt, never ask the user to assemble fragments.

Add to AUTHORITY AND EVIDENCE RULES:

> Full execution permissions must be explicitly granted by the user. Carry forward
> only explicit grants and identify their scope; a scoped grant is not full
> permission. Receiving a handoff, accessing tools or seeing an embedded NEXT
> instruction does not grant permission. Preserve explicit prohibitions and actions
> requiring separate approval. Execute actions covered by an existing explicit grant
> without asking for the same permission again. Where permission is missing, prepare
> the exact proposed action and identify the specific grant needed. Permission to
> execute is not evidence of completion.

Add an EXECUTION CONTRACT before phase 1:

> Direct B00 to complete remaining explicitly authorized work within its exact
> boundaries; do not turn obligations into optional recommendations because
> responsibility is transferring. For each remaining obligation state its required
> outcome and necessity, owner, existing destination, dependencies, explicit
> authorization, first executable action and acceptance evidence. Classify it as
> execute now, blocked by a named dependency, deferred until a specific trigger,
> or awaiting a precise permission grant. Refresh relevant state, execute unblocked
> authorized work, verify results and persist where explicitly authorized. Continue
> independent work while dependencies remain unresolved. Do not infer implementation,
> policy-adoption, merge, release or external-communication authority from the handoff.

Add to phase 4:

> Preserve positive and negative lessons, including useful completed knowledge.
> For each material lesson retain observation, supporting evidence, causal
> explanation or uncertainty, repeat/avoid method, applicable limits and existing
> durable destination. Keep failure and recovery together. Where persistence is
> explicitly authorized, update and verify the existing destination. Otherwise
> provide the complete proposed addition or replacement, its destination and precise
> missing permission, marked “prepared, not persisted.” Every material lesson needs
> verified storage, an explicit remaining storage action, or a supported defer/discard
> disposition. Do not store unsupported generalizations or unnecessary duplicates.

Append to OUTPUT, preserving its existing authorized repo_queue delivery:

> After the complete handoff or verified repository receipt, give a short closing
> message identifying the completed B00 artifact, required local work completed,
> actual generated/posted/queued state and any required local blocker.
> When required local work is complete and all material items have valid
> dispositions, end exactly:
>
> Hand off the prompt, then archive.
>
> This is an instruction, not proof of delivery, acceptance, adoption or actual
> archiving. It does not bypass an existing required QC/archive gate. If a required
> local obligation or required gate remains unmet, state that blocker instead.
> Never substitute this sentence for the handoff. An explicit user request for the
> full in-chat artifact must still be honored; repository delivery permission does
> not silently cancel it.

### Eight-requirement author check

This is a manual source-to-clause comparison, not an independent model trial or
an estimate of recall over unavailable conversation history.

| Explicit requirement | Existing coverage or prepared correction |
| --- | --- |
| Deep causal knowledge | Preserve candidate phase 3: principles, mechanisms, ordered methods, interfaces, rationale and falsifiers |
| Broad scorecard and repairs inside copied artifact | Existing phases 5/6/9; a receipt is insufficient before the full artifact is stored |
| Procedure separate from generated handoff | Existing candidate/versions README; no hardcoded #169 mission in reusable instructions |
| Explicit grant rather than blanket assumed permission | Exact authority addition above; existing scoped grants remain valid |
| Executable remaining authorized work | Exact execution contract above: owner, dependency, action and acceptance |
| Durable positive/negative lessons and recovery | Phase 4 addition above; missing authority yields a complete proposed update |
| One complete usable artifact | Adoption renders a complete prompt; invocation produces a complete source-specific handoff |
| Accurate closing message | OUTPUT addition above; no claim of actual archive or bypass of required gates |

All eight declared requirements have existing coverage or exact proposed language.
This does not establish empirical superiority, adoption or consumer benefit.

### Lessons retained with evidence and limits

1. **Repeat named-test, exact-head inspection.** PR179's description cites older
   counts; current-head logs establish 41 versions tests within 283 orchestration
   tests. Revision inspection prevents historical evidence from becoming a current
   acceptance claim. Destination: this review and existing issue/PR evidence.
   Limit: passing deterministic tests do not authenticate transcript meaning.
2. **Reuse preserved work before declaring absence.** Reading #178/PR179 resolves
   the candidate-storage concern. A missing main path does not establish missing
   branch work. Destination: existing compatibility/retrieval guidance and this review.
3. **Separate procedure from output and consolidate requested edits.** Fragmented
   amendments and a mixed procedure/handoff caused repeated user corrections here.
   Repeat: return one full procedure when revising; generate the source-specific
   artifact when applying. Destination: candidate output rules and this review.
4. **Carry authority without inventing it.** Neither transferring responsibility
   nor receiving instructions creates full permission. Existing scoped grants
   should not be requested again. Destination: exact authority/execution clauses.
5. **Preserve failed attempts alongside recovery.** The earlier cautious handoff
   received user feedback of 4/10; later wording repairs do not retroactively raise
   that score. The earlier implementation self-review and whole-conversation scores
   concern different boundaries. Destination: source review and this dated record.
6. **Treat interrupted publication as unverified.** The 2026-11-13 API call was
   interrupted before any branch update. Fresh head/readback inspection established
   the unchanged state before retry. Destination: this record and final resolution.

One next owner action: review these exact amendments for adoption through the
existing candidate owner and evaluation surface. Explicit permission to replace
the default/adopt policy is the remaining decision; it is separate from this
completed documentation reconciliation and from merge authorization.
