# _BASKET — Multi-tool routing and spark claims

**Owned by:** B00. Routing data: `orchestration/planner/agent-routing.json` (validated by `orchestration/validate_agent_routing.py`).

Tools draft work; lanes are defined only by `orchestration/sparks.json`. Routing never widens write paths.

| Tool | Best for | Entry point |
|---|---|---|
| ChatGPT | planning, source research, evidence review, project instructions | `orchestration/PROJECT_INSTRUCTIONS.md` |
| Claude Code | multi-file implementation, tests, refactors, CI repair | `CLAUDE.md` |
| Visual Studio / Copilot | local edits, debugging inside an existing branch | `.github/copilot-instructions.md` |
| Human owner | merge, tag, release, entitlements | `AGENTS.md` |

## One claim per spark
A claim is a leading `[Bxx]` title tag or a `spark:Bxx` label on an open issue/PR. `[HANDOFF X→Y]` issues are not claims. Check before launching:

    python orchestration/spark_claims.py issues.json   # exit 1 lists conflicting open items

Conflicts are evidence to resolve (resume the owner, narrow scope or hand off), not a worker count.

## Not yet automated (needs other owners)
- CI check mapping PR changed files to spark `write_paths`, plus branch protection: B01 handoff.
- GitHub Project board and backlog triage/merge decisions: human authorization.
