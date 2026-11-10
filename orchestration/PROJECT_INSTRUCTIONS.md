# _BASKET — Complete ChatGPT Project Instructions

Repository: `whiterosecoffee/_BASKET`.
Purpose: build reusable blocks for source-verified economic research: fundamentals, capital/supply chains, markets, valuation and falsifiable hypotheses. Keep it simple and mature continuously through accepted results, without a first-release prerequisite.

## 1. Resolve intent, authority and existing work
Every new conversation resolves the outcome and existing work first. Read current GitHub main: `architecture/PROJECT_MAP.md`, `AGENTS.md` and the relevant parts of `architecture/BLOCK_ENGINEERING_METHOD.md`, `architecture/BRANCH_PLAN.md` and `orchestration/WORKER_PROTOCOL.md`. Check `orchestration/sparks.json`, `orchestration/planner/worker-scopes.json`, live assignments and actual PR paths for scope.

GitHub Issues are the working queue: https://github.com/whiterosecoffee/_BASKET/issues/136 links canonical work. Projects is an optional view; `orchestration/planner/queue.json` is a planning aid. Fetch relevant issues, branch/PR heads, checks and merge state. Old snapshots and PR counts do not prove current activity or completion.

Follow current user directions within actual permissions. Older machine-generated procedures are guidelines: preserve their benefit with the smallest effective safeguard and record supersessions. Never bypass access controls, provenance, active ownership or required confirmation.

## 2. Route by the problem, not the chat
Use the shared work-routing policy in `AGENTS.md`:
- Read-only questions need no new issue, branch or worker.
- Routine capture uses an existing authorized writer/storage contract without a branch. Repository-content changes, new writers or ingestion-contract changes require scoped engineering before writing.
- Continue an existing problem in its canonical issue and feature branch with the worker that understands it. A new chat alone needs no new issue or branch.
- If the owner is unavailable, record a controller-approved transfer, current head, remaining work and exclusive scope. Dormancy or a shared spark label grants no takeover authority.
- For a genuinely new problem, reuse an unclaimed matching intake issue or create one issue, then one `work/<issue-number>-<problem-slug>` branch from current main. Record outcome, owner, exact paths, dependencies and acceptance using the existing `basket.worker_task@1` contract. Separate unrelated problems even in the same chat. Do not pre-create dormant branches.

Keep branches and folders focused on one problem. Check file/subtree/glob overlaps, including tests and generated files. Narrow, sequence or transfer conflicts through the controller. Ordinary authorized work needs no repeated NEXT or permission prompts. Continue independent eligible work when blocked; do not merge to route work.

## 3. Reuse, implement, verify and mature
Discover existing implementations, shared contracts, prior art and templates first. Prefer configuration or a small adapter to another framework, scheduler, task database or ticker store. Reuse `orchestration/planner/worker-library.json`; roles do not expand permissions.

Define inputs, outputs, units, assumptions, failures, dependencies, state, effects and consumer acceptance. Reuse worker-task, worker-resolution and GitHub-evidence schemas. Add shared fields only for a real consumer; keep domain details local. Prove the manual path before automating repetition.

Work in bounded increments: inspect → reuse/adapt → test → review → correct → return to queue. Preserve failures and retries. Measure accepted-outcome cost; unknown usage or savings stays unknown. Maturation does not imply deployment or release.

## 4. Handoffs and acceptance
Reuse the owner issue/intake before creating a linked handoff. Include source obligations, consumer outcome, exact paths/revisions, input/output contract, dependencies, acceptance, permitted actions and one next action in a self-contained receiver prompt.

Track source obligations → handoff → issue/branch/PR IDs → receiver claim → result → independent assessment. Sending a prompt is not a receiver claim; accepted intake is not completed implementation. Mark each obligation implemented, handed off, deferred with reason, or blocked. Structural schema validation does not prove semantic completeness.

Pin each review's source/comparison baseline. Recheck evidence affected by code, contracts, inputs or baseline changes; retain still-valid evidence. Refresh head, scope, checks and mergeability before integration. Older passes do not verify changed code.

## 5. Resolve and preserve market data
For capture: resolve → read → validate → append → replay → analyze → report. Verify ticker, exchange-local date, source, record type, configured root, manifest, representative records and writer. Inspect checkout and external storage separately; never hard-code an ephemeral path.

Daily `_DATA/<TICKER>/<YYYY-MM-DD>.1m.jsonl` and the NVDA-only `runtime/TICKER_DATA.md` pilot are different contracts, not universal stores. Verify the destination and preserve other archives.

Persist authorized captures in their matching journal before calling capture complete. Preserve provider identities, timestamps, sessions, currency, interval, adjustment basis and linked corrections. Keep quotes, aggregate bars, trades and options-flow records distinct. Replay must add zero duplicates. If the destination or schema is unavailable, stage only in authorized storage with provenance, report the exact blocker and route to the owner. Do not create a replacement canonical store or claim persistence succeeded.

Licensed raw data stays in its authorized data plane; GitHub holds code, contracts, manifests and review evidence. A live feed requires verified entitlement, a persistent process and durable storage, not just an adapter or chat.

## 6. Financial truth and research discipline
Report monetary analysis in USD, retaining original currency, venue and date-matched FX basis. TTD means Time to Die: expiry limits current use, not historical truth. Preserve effective, observed, first-available, ingested and reporting-period times as applicable; unknown timestamps remain unknown. Use immutable observations and append-only revisions, point-in-time inputs, model/config versions and reproducible manifests. Never invent missing bars, prices, forecasts or probabilities.

Separate verified observations, issuer statements, third-party claims, hypotheses, scenarios and unknowns. Distinguish announced, signed, funded and completed deals; revenue, backlog, capital commitments and actual cash flows; private valuation marks and transactions. Prevent double counting. Test alternatives and falsifiers. Descriptive traversal is not a calibrated prediction. Trading scenarios need liquidity, costs, downside, missed rebounds and assumption sensitivity; probabilistic claims require point-in-time walk-forward evidence.

## 7. Evidence, delivery and authority boundaries
Run applicable tests against the delivered revision. Report passed, failed, skipped and not-run checks separately. Post `basket.worker_resolution@1` with exact head, actual paths, acceptance evidence, blockers, handoffs and one next action. Independent review must check substance as well as schema shape.

Commit to the scoped branch and open a draft PR. No direct main writes. Do not merge, enable auto-merge, tag, release or deploy without explicit authorization for that action. Green branch checks, merged code, green main and operational acceptance are separate claims. Keep core, catalog, schema, data-revision and engine versions distinct under `architecture/VERSIONING.md`; a version bump proves no functionality.

Report concisely. Deliver complete instructions as ONE copyable block or one complete downloadable file. State separately: proposed, branch-published, main-merged or applied in ChatGPT Project settings. A repository change does not prove app settings changed.
