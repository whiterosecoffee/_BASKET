# Skills index (Agent Skills format)
Format: folder per skill with `SKILL.md` (frontmatter `name`, `description`; body under 500 lines; detail in `references/`), as documented on Microsoft Learn (Agent Skills, progressive disclosure) and agentskills.io. Validate with `python research/models/rotation/skills/validate_skills.py`.
Discovery: these live under B04 paths. Tools that discover skills in `.github/skills/` or `.claude/skills/` need a copy or symlink there, which is outside B04 and goes through B00.

| Skill | One purpose | Reads from | Writes |
|---|---|---|---|
| rotation-data-steward | ingest, normalise, history JSONL | vendors | prices/, history/, ratios, estimates |
| rotation-universe-hierarchy | universe and nested groups | manifest snapshot | universe/, hierarchy |
| rotation-two-point-compare | A vs B moves | history, points | comparisons/ |
| rotation-valuation-tiers | EPS, multiples, tiers | ratios, fundamentals | models/ |
| rotation-relativity-ratios | 1:x ratios and weights | history | profiles/ |
| rotation-group-sympathy | nested-group movement | returns, hierarchy | relativity/ |
| rotation-stress-rebound | 52-week position and rebound frequencies | daily ticker store | relativity/rebound_*.json |
| rotation-swap-decision | rotation scenarios | models, ratios | scenario output |
| rotation-evidence-curator | news, guidance, industry | web, filings | csv, NEWS md |
| rotation-audit-qa | gates, goldens, scoring | all | reports |

Routing is in `prompts/MASTER_MODEL_PROMPT.md` (v3). Each skill hands off to named skills only; none writes outside its listed outputs.
