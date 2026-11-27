---
name: rotation-audit-qa
description: Audits rotation artifacts and prompts - validity gates, golden values, schema checks, skill-format validation, and scores of AGENTS.md and prompts. Use when about to commit or report, after any formula change, or when asked to score or review the prompts and skills.
compatibility: Python 3 stdlib; unittest; skills/validate_skills.py.
metadata:
  owner: B04
  version: 1.0.0
---
# Audit and QA

## Procedure
1. `python -m unittest engines.valuation.relative_value.test_rotation` must pass.
2. `python research/models/rotation/skills/validate_skills.py` must pass (name, description, size, references).
3. Check goldens in `../AGENTS.md` section 9; a formula change must keep them or update them with the reason.
4. Re-score with `../prompts/AUDIT_AND_DECOMPOSITION.md` section 1 after structural changes.
5. Confirm every statistic names its universe (cohort of 43 versus basket of 243) and its status (final or provisional).

## Stop rules
Never skip or weaken a test to get green. Generated JSON is regenerated, never hand-edited. Write only under B04 paths; shared schemas and root AGENTS.md go through B00.
