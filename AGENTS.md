# _BASKET — Agent and Conversation Operating Contract

Repository: `whiterosecoffee/_BASKET`. Canonical complete, single-block ChatGPT Project Instructions: `orchestration/PROJECT_INSTRUCTIONS.md`. Release governance: `architecture/VERSIONING.md` and `architecture/version-manifest.json`. See `orchestration/sparks.json` for executable conversation spark scopes and `orchestration/README.md` for launch instructions.

## Mandatory conversation bootstrap
At the start of **each new actionable _BASKET conversation**, read this document and the current catalog on GitHub main **after PR #2 merges**. During the initial bootstrap, read them from `work/1-conversation-sparks-orchestration` (PR #2) while creating the new worker branch **from current main**, never from another worker's branch. Inspect relevant open GitHub issues and branches. Determine objective, spark, disjoint write ownership and existing dependencies. Create a **new GitHub issue for that conversation**, then create a **new unique branch** from the latest `main`, formatted `work/<issue-number>-<objective-slug>`. Record spark ID and issue/branch references in the issue and subsequent PR. Never reuse another conversation's branch. Do not pre-create branches for dormant sparks. Read-only investigation does not require edits, but still creates issue/branch when explicitly designated as a project workstream.

## File ownership is mandatory
Only change files listed in **your spark's write_paths**. Anyone may READ referenced files on main or dependencies, but cannot write another spark's domain. Path patterns identify exact file contracts rather than unrestricted access to parent directories. If an existing workstream or PR already owns the same file, stop conflicting writes and post a handoff. For overlapping schema/architecture changes, request B00 orchestration approval; do not unilaterally modify shared contracts. New files under an owned path are allowed.

Separation:
- B02 owns market history, FX and runtime ingestion; company sparks cannot edit OHLCV or live snapshots.
- B03 owns ticker `events.json`; ticker researchers submit verified event proposals, not direct writes.
- B05 owns ticker `relationships.json`; company/theme researchers submit edge proposals, not direct writes.
- Company sparks own only their respective `entity.json` and `research/<entity>/**`.
- Domain unit tests follow code ownership: B02 owns `tests/test_ttd.py`; B21 owns `tests/test_narrative.py`; new domain tests should be placed in owned module test paths or get B00/B01 ownership arbitration. B01 owns shared `tests/validate_stores.py`, `tests/integration/**` and `.github/workflows/**` only.
- B00 owns `AGENTS.md`, `orchestration/**`, `architecture/**`, `schemas/**`, root `README.md`/`CHANGELOG.md` and cross-domain contract arbitration.

## Cross-domain requests
Create an issue labeled/described as a dependency (labels if available), referencing the source issue and owner spark. Include requested contract/data change, reason, verified sources, input/output expectations, acceptance criteria and exact file scope. Provide a ready-to-paste prompt for the domain's conversation. Continue unrelated work; do not claim the receiving conversation has acted until it has retrieved the issue.

## Git, quality, data truth
No direct commits to main. Commit only to your branch; PR to main; never self-merge without authorization. Require tests and review of schema changes. Historical observations and revision records are append-only, with event/effective/available/ingested timestamps and provenance. TTD = **Time to Die**; expired data is historical, not current. Never claim continuous market refresh without authenticated entitled adapters and a persistent process. Report **USD**, retaining original currency and date-matched conversion basis. Distinguish verified facts, issuer claims, hypotheses, scenario outputs and missing evidence. Do not invent prices, ownership, contracts, fair value or probabilities.

## Required issue output
At initialization report: `Spark ID | Issue URL | Branch | Objective | Write paths | Dependencies | Next task`. A PR should state validation evidence, changed files, linked issues and outstanding handoffs. Existing archived or incomplete conversations are context, not automatic authorization to modify another scope.

## Launch discipline, state and data-plane boundary
Before starting a new work branch, read the current registry **from main if merged**, otherwise read the provisional instructions from `work/1-conversation-sparks-orchestration` (PR #2). Do not mistake the temporary read-only bootstrap source for your own development branch. Check active issue ownership and PR changed files; exact path strings alone do not protect against subtree/glob overlaps or multiple active workers using the same spark. Scope can be narrowed, but not silently expanded. Keep at most 3–5 worker conversations active initially; downstream research can proceed while data/computations are blocked, but may not claim a verified inference.

GitHub owns source code, schemas, contracts and reproducible manifests. Time-sensitive minute bars and continuous JSONL writing need a durable local or hosted data plane and entitlement-aware adapters. GitHub and ChatGPT are **not** live polling workers. Standardize event effective, observed, first available, ingested and period-end times; always separate the value's observation freshness from the lifetime of its historical truth.

## Project instruction delivery and version governance
When asked to provide or edit the project's ChatGPT Project Instructions, always provide the **complete current instructions in a single copyable block**, never fragments or only diffs. Maintain the canonical text in `orchestration/PROJECT_INSTRUCTIONS.md` on this conversation's authorized branch. Maintain separate versions for core, orchestration catalog, schemas, immutable observation revisions, engine logic and reports. Never claim v0.5.0 is released until the release gates pass, the user authorizes it, and the approved main commit is tagged. No tags/releases from worker branches.

## Standardized worker claim and resolution payload
Read `orchestration/WORKER_PROTOCOL.md` when beginning a new spark or reviewing a handoff. The worker issue contains one `basket.worker_task@1` JSON payload naming task ID, exclusive paths, dependencies and evidence-backed acceptance criteria. Before final reporting, post a `basket.worker_resolution@1` payload into the worker issue or PR with the current head SHA, actual tests, unchanged/changed paths, missing checks, blockers, cross-domain handoffs and ONE next action. Use null for unknowable timestamps. B00 verifies each claim against a freshly fetched GitHub issue, changed-file list, PR head SHA and workflow result. Component-complete/green branch work is NOT integrated main. Never claim a run executed unless a real runner produced evidence. Do not overwrite another worker's task/report.

## Reusable worker planner and task queue
B00 owns `orchestration/planner/queue.json` (planned objectives), `orchestration/planner/worker-library.json` (reusable capabilities/profiles/recipes), `orchestration/planner.py` and `orchestration/github_snapshot.py`. Before allocating a new spark, consult the live GitHub-backed plan, then select ONE priority objective. A single worker may compose multiple reusable capability profiles, but its modifications must stay exclusively inside the assigned spark's write paths. Roles and recipes are reusable; **GitHub issue and branch identities never are**.

The queue is an ordered proposal, not an authoritative live completion ledger: issue status, actual PR file changes, CI conclusions and current merge state must be fetched anew. Never infer the number of active conversations from open PRs; report worker capacity unknown until corroborated. Do not launch duplicate workers for incomplete existing issues: resume their owning chat if available or issue a new documented handoff with a new issue/branch. No automatic merge, tag, or new ChatGPT conversation creation.

## Worker task learning and QC
Every worker reads its compiled task scope in `orchestration/planner/worker-scopes.json`, including exact job, authorized paths, recipe steps, dependencies and acceptance. Record failed and successful attempts with objective evidence and retry lineage. Preserve failures; only promote corrective procedures after successful retesting. Never infer durations or optimization from unmeasured data; reusable roles do not expand access. See `orchestration/planner/WORKER_JOBS.md` and `schemas/worker-attempts.v1.json`.
