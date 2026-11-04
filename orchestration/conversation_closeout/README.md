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
