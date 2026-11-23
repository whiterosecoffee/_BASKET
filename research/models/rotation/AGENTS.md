# AGENTS.md: Two-Point Evaluation and Comparison
Scope: `research/models/rotation/**` and `engines/valuation/rotation/**` (spark B04). This file adds rules for agents that compare **point A with point B**. It does not override the repository-root `AGENTS.md`; where they conflict the root file wins. Version 1.2.1.
Key words MUST, MUST NOT, SHOULD follow RFC 2119.

## 1. Purpose
Evaluate how a price moved between two named points, compare that move across instruments and against references (NVDA, MSFT, SMH, QQQ), and report facts, assumptions and flags without forecasting. Typical pair: `fri_close` (A) vs `mon_high` (B).

## 2. Definitions
- **Point**: `{label, instrument, date, field, status}` where field is open/high/low/close/last and status is `final`, `provisional` or `derived`. A point has exactly one price, in the adjustment basis stated in the output.
- **Pair**: ordered (A, B). `change = B/A - 1`. Direction matters; never swap A and B to make a number look better.
- **Peak / extreme**: a maximum or minimum over a path. It is selected after the fact, so it overstates what was holdable (selection bias).
- **Provisional**: any value from a session that has not closed. It can still change.
- **Cohort**: the set of instruments compared in one run; benchmarks (MSFT, SMH, QQQ) are reported but excluded from cohort statistics.

## 3. Point registry (`pointcompare.POINTS`)
`thu_close`, `fri_low`, `fri_high`, `fri_close` (final); `mon_open`; `mon_high`, `mon_low`, `mon_last` (provisional while the session is open). New points MUST be added to the registry with a definition and a status before use.

## 4. Required inputs and checks (validity gate)
An evaluation is INVALID, and MUST say so instead of reporting numbers, if any check fails.
| # | Check |
|---|---|
| V1 | A and B come from the same adjustment basis (Massive adjusted aggregates) and the same share basis (split-normalised; SNDK 8-for-1 effective 2026-11-20). |
| V2 | Every provisional point is labelled provisional in the output, with the snapshot time. No provisional value is called a close. |
| V3 | A is not later than B, unless both are realised prices of the same session (e.g. low then high) and the pair is labelled a path comparison. |
| V4 | Screenshot or typed-in prices are cross-checks only. Compare them with Massive; flag differences above 0.5% and use Massive. |
| V5 | Instruments missing either point are listed as excluded, never imputed. |
| V6 | Cohort statistics exclude benchmarks and state n. |
| V7 | Data older than the stated cut-off, or estimates older than 120 days, are not used for current claims. |
| V8 | Headline-sourced event descriptions are marked secondary and unverified. |

## 5. Required metrics for every pair
Price track (facts):
1. `change = B/A - 1`.
2. Context points: `b_vs_thursday_close`, `b_vs_friday_high`, `b_vs_friday_low`.
3. `share_of_friday_drop_recovered_at_b = (B - fri_close)/(thu_close - fri_close)` when the prior day's drop is positive.
4. When B is a peak: `giveback_from_b_to_last = last/B - 1` and `giveback_share_of_move = (B - last)/(B - A)`; `last_position_in_friday_low_to_b_range`.
5. Flags: `monday_low_held_above_friday_low`, `gap_unfilled` (session low above the prior high), `peak_at_open_proxy` (high within 0.1% of the open; a proxy, because no intraday timestamps are stored).
6. Cohort context: rank, median, and the theme median of the same metric.
Relationship track (facts): ratios `x = P_subject / P_reference` at A and at B for each of NVDA, MSFT, SMH, QQQ, with the change in x and its position in the 250-day band (see `profiles/<T>.json`).
Valuation track (separate from the price track): if no estimate, guidance or fundamental changed between A and B, the whole `change` is a multiple modifier; otherwise label it mixed and cite the event (`multiple_events.csv`). Never present a mixed move as pure re-rating.
Multiple track (`cli multiples`, schema `rotation.multiples/1`): record P/E at A and B with EPS held fixed at the latest TTM, so the difference is pure price. P/E is undefined when EPS <= 0; then record P/S and EV/S. State the EPS basis (cohort: Massive ratio EPS; subjects also split-normalised GAAP TTM and a forward basis), and report "max compression" (`fri_low`) and "peak rebound" (`mon_high`) together with `turns_added` and `expansion`. For a 52-week-peak comparison show the P/E on the EPS known then and on today's EPS.
Tier track (`cli models`, `prompts/MASTER_MODEL_PROMPT.md` section 3): when a pair spans an EPS update, report the tier of each point before and after the update at the same price, and label bounds `point_in_time` or `constant_current_E_counterfactual`.
Zone track: dwell days, visits and volume share of the corridor [A, B] in the prior history, and the number of prior crossings of each level (supports reading a move as passing through an "air pocket" or a heavily traded zone).

## 6. Interpretation rules
- A peak comparison MUST be paired with the A-to-last change. Report both; do not lead with the peak.
- Do not annualise, extrapolate, or treat B as a target or as support/resistance. A one-session move is not a trend.
- Compare a single name with its theme and the cohort before calling it special: a market-wide flush and rebound moves most names.
- A name that lags its theme (e.g. SNDK versus MU/SKHY/WDC/STX) is a lead to explain, not a signal.
- Use "reported", "assumed", "measured" and "scenario" for the five evidence classes: verified fact, issuer claim, secondary report, assumption, scenario output.
- No personalised investment advice, no buy/sell instruction.

## 7. Procedure
1. Fix the pair and the snapshot time; state it.
2. Run the validity gate (section 4). Stop on failure.
3. `python -m engines.valuation.rotation.cli compare --a <A> --b <B>` writes `comparisons/<A>__vs__<B>__<date>.json` (schema `rotation.compare/1`).
4. Join with `profiles/<T>.json` for ratios, zones and valuation context; keep valuation and price tracks separate in the write-up.
5. Report: (a) pair and status, (b) the three subjects (NVDA, CRWV, SNDK) first, (c) cohort summary and theme table, (d) flags, (e) limitations, (f) files and as-of times.
6. Refresh when a provisional session closes: regenerate with final points, keep the old snapshot file, and state what changed.

## 8. Output contract (`rotation.compare/1`)
Top level: `schema`, `comparison_id`, `point_a`, `point_b`, `context_points`, `as_of_et`, `monday_snapshot_file`, `provisional`, `provisional_note`, `adjustment_basis`, `selection_bias_warning`, `subjects`, `cohort_summary`, `theme_summary`, `ranking_by_change`, `per_ticker[]`. Each `per_ticker` item has `ticker`, `theme`, `points{}`, `comparison{}` with the metrics in section 5. A consumer MUST read `provisional` before using any number.

## 9. Golden examples (regression)
Snapshot `massive_mon_20261123_1351ET.csv`, pair `fri_close` -> `mon_high`:
- NVDA 125.53 -> 171.50, change +36.62%; recovered 224.8% of the Friday drop at the peak; last is 4.0% below the peak (15.1% of the move given back).
- CRWV 39.51 -> 51.90, +31.36%.
- SNDK 79.24 -> 99.07, +25.03%; gave back 50% of the move by the snapshot.
- Multiples (EPS held fixed), `fri_low` -> `mon_high`: NVDA trailing P/E 15.6 -> 21.5 on Massive EPS 7.99, and 13.4 -> 18.4 on GAAP-normalised TTM EPS 9.31; SNDK 4.6 -> 5.8 on Massive EPS 17.06.
- Tiers (point-in-time): NVDA multiple range 13.4 to 48.1 on E 9.31; Friday low and close in T1, Monday last in T2; the 2026-11-17 EPS update (+18%) moved the unchanged price from T2 to T1. Relativity: 9 of 43 cohort equities set a new 52-week low on 2026-11-20 (the cohort is a selection-biased screenshot list); across the 243 priced basket names 39 did (`universe/low52w_friday_classification.csv`).
Any change to the formulas MUST keep these values or update this section with the reason.

## 10. Testing and change control
- Run `python -m unittest engines.valuation.rotation.test_rotation`; the `PC` and `C` test classes cover this contract.
- Generated JSON is regenerated, never hand-edited. Input snapshots are append-only; new snapshots get a new file name with the time in it.
- Write only under B04 paths. Changes to shared schemas or the root `AGENTS.md` go through B00.
- Bump the version in this file for any change to definitions, validity checks or required metrics.
