# _BASKET — Agent and Conversation Operating Contract

Repository: `whiterosecoffee/_BASKET`. See `orchestration/sparks.json` for executable conversation spark scopes and `orchestration/README.md` for launch instructions.

## Mandatory conversation bootstrap
At the start of **each new actionable _BASKET conversation**, read this document and the current catalog on GitHub main; inspect relevant open GitHub issues and branches. Determine objective, spark, disjoint write ownership and existing dependencies. Create a **new GitHub issue for that conversation**, then create a **new unique branch** from the latest `main`, formatted `work/<issue-number>-<objective-slug>`. Record spark ID and issue/branch references in the issue and subsequent PR. Never reuse another conversation's branch. Do not pre-create branches for dormant sparks. Read-only investigation does not require edits, but still creates issue/branch when explicitly designated as a project workstream.

## File ownership is mandatory
Only change files listed in **your spark's write_paths**. Anyone may READ referenced files on main or dependencies, but cannot write another spark's domain. Path patterns identify exact file contracts rather than unrestricted access to parent directories. If an existing workstream or PR already owns the same file, stop conflicting writes and post a handoff. For overlapping schema/architecture changes, request B00 orchestration approval; do not unilaterally modify shared contracts. New files under an owned path are allowed.

Separation:
- B02 owns market history, FX and runtime ingestion; company sparks cannot edit OHLCV or live snapshots.
- B03 owns ticker `events.json`; ticker researchers submit verified event proposals, not direct writes.
- B05 owns ticker `relationships.json`; company/theme researchers submit edge proposals, not direct writes.
- Company sparks own only their respective `entity.json` and `research/<entity>/**`.
- B01 owns shared test suite and CI workflows; code workers provide reproducible test requests and can validate locally without modifying those paths.
- B00 owns `AGENTS.md`, orchestration docs and cross-domain contract arbitration.

## Cross-domain requests
Create an issue labeled/described as a dependency (labels if available), referencing the source issue and owner spark. Include requested contract/data change, reason, verified sources, input/output expectations, acceptance criteria and exact file scope. Provide a ready-to-paste prompt for the domain's conversation. Continue unrelated work; do not claim the receiving conversation has acted until it has retrieved the issue.

## Git, quality, data truth
No direct commits to main. Commit only to your branch; PR to main; never self-merge without authorization. Require tests and review of schema changes. Historical observations and revision records are append-only, with event/effective/available/ingested timestamps and provenance. TTD = **Time to Die**; expired data is historical, not current. Never claim continuous market refresh without authenticated entitled adapters and a persistent process. Report **USD**, retaining original currency and date-matched conversion basis. Distinguish verified facts, issuer claims, hypotheses, scenario outputs and missing evidence. Do not invent prices, ownership, contracts, fair value or probabilities.

## Required issue output
At initialization report: `Spark ID | Issue URL | Branch | Objective | Write paths | Dependencies | Next task`. A PR should state validation evidence, changed files, linked issues and outstanding handoffs. Existing archived or incomplete conversations are context, not automatic authorization to modify another scope.
