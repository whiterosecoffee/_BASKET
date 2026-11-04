# Conversation closeout audit — B00 draft

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

Markdown containing completion disposition, optional evidence-weighted quality score, up to three lessons, and (when required) a complete copyable handoff. Final line is exactly one of: `Continue here`, `Decision needed`, `Hand off before archiving`, `Ready to Archive`.

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

Say: **"Run _BASKET closeout review. Extract reusable principles and execution lessons, score observable execution, finish authorized work, and prepare the evidence JSON for the repo closeout command. Generate the full handoff prompt if work remains."**

If ChatGPT cannot execute the repo command, it can still perform the review in-chat and produce the same evidence JSON. Do not claim a CLI run occurred.

## Orchestrator integration (proposed)

B00 may register an alias `basket closeout --input <file> --output <file>` in the **existing** command/router system, delegating to this module. Do not add a second scheduler or queue. B01 should independently test the CLI after B00 accepts the contract. Existing `basket.worker_task@1` and `basket.worker_resolution@1` remain authoritative for worker claims; this report never replaces them.

## Evidence and knowledge extension (draft)

Optional `claims` is an array of objects with `id`, `type`, `text`, and for `repository_verified` or `independent_test`, mandatory `source_ref` and `revision`. Types: `user_assertion`, `conversation_observation`, `repository_verified`, `independent_test`, `inference`, `proposal`, `unknown`. The CLI validates the presence of references but **does not fetch or authenticate them**.

Each insight may additionally contain `pattern`, `methodology`, `application`, `evidence`, `limitations`, `architecture`, `capability_match`, `rationale` and `claim_ids`. The report preserves these details and includes top principles in transfer prompts. A referenced claim ID must exist in the supplied claim array. An evidence string alone does not constitute independent verification.

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
