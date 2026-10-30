# _BASKET — Operating architecture (multi-author, multi-tool)

**Owned by:** B00. Describes how work flows; data and engine contracts live in `basket.architecture.json` and `schemas/`.

## Layers
| Layer | Holds | Authority |
|---|---|---|
| Control | `AGENTS.md`, `orchestration/` (sparks, planner, protocol, routing) | B00 |
| Contracts | `schemas/`, `architecture/` | B00 |
| Data plane | `runtime/`, `fx/`, `tickers/*/history*`, `live/`, `intraday/` | B02 |
| Domain data | `tickers/*/events.json` (B03), `relationships.json` (B05), `entity.json` and `research/<entity>/` (company sparks) | owning spark |
| Engines | `engines/<module>/` per `orchestration/MODULE_STANDARD.md` | owning spark |
| Gates | `.github/workflows/`, `tests/validate_stores.py`, `tests/integration/` | B01 |

## Work flow
1. Owner or B00 picks one objective from the planner using fresh GitHub evidence.
2. One issue and one `work/<issue>-<slug>` branch per task, from latest `main`.
3. Any tool (ChatGPT, Claude Code, Visual Studio/Copilot) works inside that spark's `write_paths` only, starting from `orchestration/AGENT_INSTRUCTIONS.md`.
4. Cross-lane needs become a `[HANDOFF X→Y]` issue.
5. Worker posts `basket.worker_resolution@1`; B01 CI must pass on the exact head SHA.
6. Human owner reviews and merges. Nobody merges their own PR; no auto tags or releases.

## Setup
Python 3.12, standard library only; no install step. From the repository root:

    python tests/validate_stores.py
    python orchestration/validate_sparks.py
    python orchestration/validate_agent_routing.py
    python orchestration/validate_agent_entrypoints.py
    python orchestration/validate_module_structure.py
    python -m unittest discover -s orchestration/tests -p 'test_*.py'
    python -m unittest discover -s tests/integration -p 'test_*.py'

GitHub-side setup (board, labels, `main` ruleset) is in `orchestration/PROJECT_BOARD.md`.

## Known gaps
- New validators are not yet in `.github/workflows/validate.yml` (B01).
- `engines/*` modules do not yet follow `MODULE_STANDARD.md` (owning sparks).
- No CI check yet maps PR changed files to `write_paths` (B01).
