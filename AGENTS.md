# _BASKET — Agent Operating Contract

Repository: `whiterosecoffee/_BASKET`. Start at `architecture/PROJECT_MAP.md` on current main. Complete ChatGPT Project Instructions: `orchestration/PROJECT_INSTRUCTIONS.md`. Detailed evidence protocol: `orchestration/WORKER_PROTOCOL.md`. Reuse the existing spark catalog, worker schemas, capability library and domain implementations rather than adding parallel systems.

## Work-routing policy

This section is the shared routing rule referenced by the Project Instructions and Worker Protocol. It supersedes older conversation-per-branch bootstrap text and dated launch priorities. Current user directions and recorded controller assignments govern work within actual permissions. Older machine-generated procedures are guidelines: preserve their intended benefit with the smallest effective safeguard, record material supersessions and retain history. They cannot waive access controls, evidence requirements or required confirmation.

1. **Read-only:** a question or investigation creates no issue or branch merely because it starts a new chat.
2. **Routine capture:** an existing authorized data-plane writer may capture/replay under its existing contract without a development branch. Resolve its actual destination and scope first. The first repository-content mutation, new writer or ingestion-contract change enters scoped engineering before writing.
3. **Existing problem:** continue its canonical issue and feature branch; hand work to the branch worker that understands it. New chats and resumed sessions do not reset task identity. A completed or unrelated problem is not an excuse to expand that branch.
4. **Owner transfer:** if continuation by the owner is unavailable, record a controller-approved transfer, current head, remaining obligations, exact paths and exclusive writer before proceeding. Do not take over from a stale status or a shared spark name. Release or sequence competing writes.
5. **New problem:** reuse a matching unclaimed intake issue, or create one canonical issue, then create one `work/<issue-number>-<problem-slug>` branch from current main. Establish acceptance and `basket.worker_task@1` before content writes. A genuinely distinct feature gets its own branch even within the same conversation. Never pre-create dormant branches.
6. **Cross-owner work:** use the existing receiver issue/intake and a self-contained handoff; create a linked issue only if no suitable record exists. A controller may narrow, sequence or transfer scope within delegated authority. Ordinary authorized work does not require another user approval round trip. Do not merge merely to route work.

## GitHub queue and write ownership

GitHub Issues are the authoritative working queue; start at issue #136 and follow canonical owner issues. Projects is an optional projection. `orchestration/planner/queue.json` is a historical/planned view, not another live ledger. Retrieve relevant current issues, branch heads, actual PR paths and checks. Open PR count is not active-worker capacity.

Before writing, compare the current assignment with `orchestration/sparks.json`, `orchestration/planner/worker-scopes.json` and live claims. Inspect file, subtree and glob overlaps, including tests, schemas and generated output. Scope may narrow; expansion or transfer must be recorded. A reusable role or broad domain label does not confer exclusive write authority. Resolve stale catalog wording through this routing policy and the catalog owner; do not silently edit another worker's files.

Default domain separation:
- B00: shared architecture, schemas, orchestration and contract coordination.
- B01: `.github/workflows/**`, shared `tests/validate_stores.py` and `tests/integration/**`.
- B02: market history, FX and ingestion/runtime; domain tests include `tests/test_ttd.py`.
- B03: canonical ticker `events.json`; B05: canonical `relationships.json`.
- B06: traversal; B21: narrative and falsification, including `tests/test_narrative.py`.
- Company researchers: only explicitly assigned issuer entity/research paths. Propose canonical events or edges to their owners rather than writing them directly.

Domain unit tests follow the implementation owner. Resolve unmatched or shared paths through the controller. Begin with one implementation lane and targeted independent verification; increase concurrency only with confirmed capacity, disjoint writes and evidence that coordination works.

## Small reusable blocks and complete handoffs

Follow `architecture/BLOCK_ENGINEERING_METHOD.md` and `architecture/BRANCH_PLAN.md`. Reuse existing contracts, templates and maintained prior art. Define inputs, outputs, units, assumptions, errors, dependencies, owned state and effects. Prefer one small adapter or pure check to a new framework. Keep branches and folders focused on one coherent problem.

Handoffs preserve source obligations, exact source/target revisions and paths, consumer outcome, dependencies, acceptance and a ready-to-use receiver prompt. Trace source obligations → handoff → issue/branch/PR IDs → explicit receiver claim → result → independent assessment. Accepted intake is not implementation completion. Structural validation does not establish semantic completeness. Resolve or explicitly defer every obligation; do not omit it from a shorter prompt. Continue independent eligible work while an item is blocked.

## Market data and source truth

Resolve → read → validate → append → replay → analyze → report. Verify ticker, exchange-local date, source, record type, configured root, representative record and writer before capture. The external `_DATA/<TICKER>/<YYYY-MM-DD>.1m.jsonl` layout and the NVDA-only pilot in `runtime/TICKER_DATA.md` are separate contracts, not universal destinations. Missing access never grants authority to create another canonical store.

Persist authorized captures before reporting capture complete; retain source IDs, timestamps, sessions, currency, interval, adjustment basis and append-only corrections. Verify duplicate-free replay. If destination or schema is unresolved, stage only in authorized storage with provenance and report the exact blocker to the owner. Documentation or fixture tests do not prove a production writer ran.

GitHub holds code, schemas and manifests; licensed raw data belongs in its authorized durable data plane. A live feed requires an entitled provider, persistent worker and verified operation. Report **USD** with original currency and date-matched FX basis. TTD = **Time to Die**; expired observations remain history, not current evidence. Separate effective, observed, first-available, ingested and period-end times. Distinguish facts, issuer claims, hypotheses, scenarios and missing evidence. Do not invent prices, ownership, contracts, fair value or probabilities.

## Verification and continuous maturation

Reuse `basket.worker_task@1`, `basket.worker_resolution@1` and `basket.github_evidence@1`. Claims name the canonical issue, feature branch, exact scope, dependencies and testable acceptance. Results identify actual changed paths, exact head, actual tests, missing checks, blockers, handoffs and one next action. Use null for unknowable timestamps. B00 independently fetches relevant GitHub evidence and assesses acceptance; self-report or schema validity alone is insufficient.

Pin the source and comparison baseline. Changed code, contracts, inputs or baseline invalidate affected evidence; preserve still-valid evidence and explain what needs rechecking. Refresh exact-head checks and scope before integration. Preserve failures, corrections and measured retry lineage. Do not invent efficiency or duration measurements. Follow `orchestration/planner/WORKER_JOBS.md` for applicable attempt evidence.

Mature continuously through bounded accepted increments. No first-release milestone blocks useful independent work. Commit only to the scoped branch and open a draft PR. No direct main writes. No merge, auto-merge, tag, release or deployment without explicit authorization. Branch pass, merged main, main CI and operational acceptance remain distinct. Version policy in `architecture/VERSIONING.md` still governs actual releases; no version declaration proves operation.

## Instruction delivery

Maintain complete `orchestration/PROJECT_INSTRUCTIONS.md` text, not isolated amendments. Deliver it as ONE copyable block or one complete downloadable file. Separately state branch/main/application status. A repository commit is not proof that ChatGPT Project settings were changed. Do not overwrite other workers' claims or reports.
