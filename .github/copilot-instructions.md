# _BASKET — Agent entry point (identical for every tool)

This exact text is the entry point for ChatGPT, Claude Code, Visual Studio/Copilot and any other agent. `CLAUDE.md` and `.github/copilot-instructions.md` must be byte-identical copies of this file; `python orchestration/validate_agent_entrypoints.py` enforces it. Change this file first, then copy it.

`AGENTS.md` is the binding operating contract; read it first, then `orchestration/AGENT_ROUTING.md` and `orchestration/MODULE_STANDARD.md`.

- One GitHub issue and one new `work/<issue-number>-<objective-slug>` branch per task, cut from latest `main`. Never commit to `main` or merge your own PR.
- Write only inside your spark's `write_paths` in `orchestration/sparks.json`; if another open issue/PR owns the file, stop and post a handoff issue instead.
- Never invent prices, ownership, contracts or probabilities; report USD and keep provenance and timestamps.
- Every module follows `orchestration/MODULE_STANDARD.md`.
- Before the final report, post a `basket.worker_resolution@1` payload (`orchestration/WORKER_PROTOCOL.md`) with the real head SHA and test evidence.
- For orchestration changes run `python orchestration/validate_sparks.py` and `python -m unittest discover -s orchestration/tests -p 'test_*.py'`.
