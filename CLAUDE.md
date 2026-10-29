# _BASKET — Claude Code entry point

`AGENTS.md` is the binding operating contract; read it first, then `orchestration/AGENT_ROUTING.md`.

- One GitHub issue and one new `work/<issue-number>-<objective-slug>` branch per task, cut from latest `main`. Never commit to `main` or merge your own PR.
- Write only inside your spark's `write_paths` in `orchestration/sparks.json`; if another open issue/PR owns the file, stop and post a handoff.
- Before final report, post a `basket.worker_resolution@1` payload (see `orchestration/WORKER_PROTOCOL.md`) with the real head SHA and test evidence.
- Run `python orchestration/validate_sparks.py` and `python -m unittest discover -s orchestration/tests -p 'test_*.py'` for orchestration changes.
