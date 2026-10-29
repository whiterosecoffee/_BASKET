# _BASKET — Copilot / Visual Studio entry point

`AGENTS.md` is the binding operating contract; read it first, then `orchestration/AGENT_ROUTING.md`.

- Work only on the branch `work/<issue-number>-<objective-slug>` of an existing issue; never commit to `main` or merge.
- Edit only files in your spark's `write_paths` (`orchestration/sparks.json`). Cross-domain needs become a linked handoff issue.
- Never invent prices, ownership, contracts or probabilities; report USD and keep provenance and timestamps.
- Report results with a `basket.worker_resolution@1` payload (`orchestration/WORKER_PROTOCOL.md`).
