# Macro backdrop partition — local agent contract (B17)

Scope: this directory only (`research/composites/macro_backdrop/**` and its tests under `engines/composites/macro_backdrop/**`). It adds to, and never overrides, the root `AGENTS.md` and `orchestration/PROJECT_INSTRUCTIONS.md`. Where they conflict, the root files win and the conflict is reported first.

Owner: spark B17 (Cross-Market Signal Composite). Origin: issue #141, PR #142.

## Partition logic and naming (T08)
| Layer | File | Holds | Mutability |
|---|---|---|---|
| Register | `macros.v1.json` | what is tracked, how it is computed, routing, access status, TTD, hypothesis thresholds | versioned; meaning change = new major file |
| Resources | `resources.v1.json` | scarce-resource and chokepoint-exposed measures (diesel and other distillates, LNG, fertilizer, sulfur, aluminum, helium) | versioned; same rule |
| Snapshot | `snapshots/YYYY-MM-DD.json` | dated observations with evidence class, data age and TTD | append-only; a correction is a new file |
| Method | Claude Project doc `claude/macro-backdrop-template.md` | how an analysis is run | lives outside the repo |

Measure ids are stable: C contrast, I intraday, F futures, IX index, R rates and policy, E energy, D dollar, V volatility, S scarce resource. Never reuse or renumber an id.

## What an agent may do here
- Add measures, sources, or snapshots inside the paths above.
- Label every threshold `hypothesis` with a set date and rationale.
- Record unretrieved or unentitled data as `unknown` / `not_entitled`. Never infer one series from another.

## What an agent may not do
- Write outside the paths above. Schema registration (`schemas/**`) is B00's. CI wiring (`.github/workflows/**`, shared validators) is B01's. Market history and feeds are B02's. The prediction ledger is B07's.
- Edit `market_context` work (#100/#101) or any other spark's files. Use a handoff issue.
- Store probabilities, forecasts, fair values or trade instructions. Scenario ordering is ordinal and is a hypothesis for the B07 ledger.
- Put dated observations in a register file, or edit an existing snapshot.
- Claim a check ran in CI when only a local run exists.

## Evidence and freshness
- Evidence classes: verified observation, company statement, inference, scenario, unknown. Claims by belligerents (IRGC, Houthis) are company statements, not observations.
- `access_status` carries how well a figure was verified. A figure is actionable only when status is `verified` or `cross_checked` and its TTD has not expired.
- Every snapshot item carries data age and a TTD. Price levels expire at their session close. Weekly statistics expire at the next scheduled release.
- Report in USD. Keep the original unit (gallons, barrels, million tons) beside it.
- Nathan's typed prints are the live anchor. Provider data supplies history and volume.

## Refresh procedure
1. Pull daily bars for the contrast ETFs from the provider. Compute each ratio, its 21-session average and the pair's own 30-calendar-day sigma. Method is in `macros.v1.json` under `conventions.ratio_z21`.
2. Read each measure's `access` block. Re-verify anything older than its TTD.
3. Write a new `snapshots/<date>.json`. Never overwrite.
4. Run the register test before commit.

## Test
`python3 -m unittest engines.composites.macro_backdrop.tests.test_macros_register`

## Handoffs still open
- B00: register the proposed schema id `basket.macro_register@1` (unregistered here).
- B01: discover this test in shared CI.
- B02: confirm provider entitlement for VIX, futures and index series; resolve the feed-latency conflict (KC1 in the register).
- B07: take the scenario ordering from each snapshot as unresolved hypotheses.
