# _BASKET — Progress checkpoint

**Checkpoint date:** 2026-10-17. Historical snapshot from GitHub; rerun the on-demand planner for live status. This file is not a persistent monitor.

**Outcomes:** [goals.json](goals.json) · **Ordered tasks:** [queue.json](queue.json) v1.1.0 · **Exclusive scopes:** [worker-scopes.json](worker-scopes.json) · **Launch packets:** [NEXT_BATCH.md](NEXT_BATCH.md)

| Milestone | Acceptance checkpoint | Verified state | Next action |
|---|---|---|---|
| M-001 Core foundation | B05/B00/B01 merged with integrated strict CI | **Integrated and verified**: PRs #10/#2/#13; main Actions [38990763024](https://github.com/whiterosecoffee/_BASKET/actions/runs/38990763024) PASS on `5bf7fc14e2577e479279efdedfeae4b90bf85820` | Keep complete; don't re-open repair |
| M-002 Worker QC | Mandatory planner, goals, scopes, attempts, protocol and adversarial tests in CI | **Open / unverified**; handoff [#6](https://github.com/whiterosecoffee/_BASKET/issues/6) | Next NEW B01 session T-009 after worker slot available |
| M-003 Market and issuer replay | B02/B03 actual replay/negative tests and coverage | **In progress**; [B02 PR #15](https://github.com/whiterosecoffee/_BASKET/pull/15), [B03 PR #14](https://github.com/whiterosecoffee/_BASKET/pull/14) draft and incomplete | Resume same worker conversations T-004/T-005; fix and retest |
| M-004 Revenue/capital reconciliation | B19 research + B05 funded/OpenAI reconciliation + B09 holdings | **Partially started**; [B19 PR #18](https://github.com/whiterosecoffee/_BASKET/pull/18) draft; B05 handoff [#16](https://github.com/whiterosecoffee/_BASKET/issues/16) open | Resume B19 T-010 now, schedule B05/B09 when upstream accepted |
| M-005 Narrative and traversal | Source-verified falsification and 5/20/60/200-session range | **Not yet independently accepted** | B21 T-006 when slot free, B06 T-007 after B02 integrated |

**Milestones fully verified:** 1 of 5. This is a checklist count, NOT a measured percentage of engineering completion.

**Next development lanes:** Resume B02 #11 and B03 #12, and B19 #17 if those are indeed the conversations currently writing. GitHub alone does not prove activity; no extra worker capacity should be inferred. The next NEW worker is B01 T-009, then B21 T-006. No task branch is pre-created.

**QC loop:** Every failed attempt stays associated with its task and owner. Close a milestone only after its own acceptance tests, evidence/TTD checks and relevant main CI pass. Explicitly document unsupported sources, provider entitlements and unknown timings.

## Worker log — multi-tool control (B00, branch `copilot/control-repo-and-project-flow`)

Not a milestone; this is the self-closing record for one worker session on 2026-10-30. No issue number exists for it yet, so the `basket.worker_resolution@1` payload cannot be posted or validated until the owner creates the B00 issue.

| Item | State | Evidence |
|---|---|---|
| Identical agent entry point (`orchestration/AGENT_INSTRUCTIONS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`) | Done on branch | `python orchestration/validate_agent_entrypoints.py` |
| Agent routing table and one-claim-per-spark check | Done on branch | `validate_agent_routing.py`; `orchestration/tests/test_agent_routing.py` |
| Standard module structure (`MODULE_STANDARD.md`) | Standard added; existing `engines/*` modules do not conform | `validate_module_structure.py` lists gaps (exit 0 unless `--strict`) |
| Project board runbook (`PROJECT_BOARD.md`) | Written; board, labels and ruleset NOT created | Owner-only GitHub settings |
| Unit tests | 67 pass locally | `python -m unittest discover -s orchestration/tests -p 'test_*.py'` |
| CI on PR head | Not run or not verified | Needs a fresh Actions result on the exact head SHA |

**Open handoffs:** B01 wires the two new validators into `validate.yml` and adds a path-ownership check; B04/B06/B21/B02 close module-structure gaps; owner creates the B00 issue, the board and labels, and decides on merge. B00 does not merge its own PR. Disposition: `component_verified` locally only, not integrated.

**Next action:** owner creates the B00 issue and links it to the PR.
