# Related work and boundaries (B04 relative-value / rotation core)
Checked against `origin/main` 7eb29bb and the open draft PRs on 2026-11-26. Statuses are GitHub facts at that time; they change. Each row says what overlaps, who owns what, and what this branch does about it. Nothing here edits another worker's files.

| PR / branch | Spark | What it does | Overlap with this branch | Boundary and action |
|---|---|---|---|---|
| #298 `work/297-rotation-bid` | B04 | Held-bid threshold: cost- and spread-aware required bid for a forward-value rotation (`engines/valuation/rotation/rotation.py`, `example.json`, `feature-design.md`) | Same spark, and it wrote the same file path `engines/valuation/rotation/rotation.py` as this branch did | **This branch renamed its package to `engines/valuation/relative_value/`**, so the two cannot collide. #298 owns execution thresholds (bid, ask, slippage, whole shares); this branch owns the valuation gap signal, swap identity, tiers and relativity. Handoff posted on #298. |
| #308 `work/305-optical-architecture-relationships`, #313 `work/312-floating-rotation-review` | B15 | Optical relationship map, floating-rotation contract and review of its source | Rotation tool contract in the optical theme folder | Read-only. This branch does not write under `research/themes/**`. Its relationship weights (NVDA, MSFT, SMH, QQQ) are statistical, not the B15 supply-chain map; they should be reconciled by a handoff, not merged. |
| #301 `work/300-sftby-capital-conversion-rotation` | B09 | SFTBY capital-conversion rotation prototype | Rotation vocabulary | Separate domain (holdings and NAV). No shared files. |
| #307 `work/306-avgo-cumulative-growth` | B04 | AVGO research and initial semiconductor vETF evidence snapshot | "Virtual ETF" concept | Same spark, different paths (`research/AVGO/**`). Its evidence is an input to this toolkit's `estimates.csv`, not duplicated here. |
| #294, #296, #292, #304 (TEAM, STX, MRVL, WDC) | B04 | Per-ticker earnings calendars and EPS growth outlooks 2026-2030 | Forward EPS by ticker | Source of per-ticker forward EPS. This branch reads their conclusions as inputs; it does not recompute them. |
| #319 `work/318-qqqe-rebound` | B17 | QQQE drawdown and rebound potential | Same question as `rebound.py` (drawdown and rebound) | B17 owns the QQQE composite. `rebound.py` is a per-ticker cross-section over the daily store. Compare outputs before either claims a result. |
| #321 `work/320-amba-memory-shock` | B19 | Ambarella DRAM shortage and selloff | Event evidence for `multiple_events.csv` | Input only. |
| `engines/valuation/etf_forward` on `work/126-etf-forward-valuation` | B04 | ETF forward valuation engine (33 commits ahead of main) | Forward-multiple method | Unmerged. Reconcile calendarization conventions before either merges. |
| `_PATTERNS` `_TOOLS/ticker_*.py`, `_TICKERS/<T>/snapshots/` | patterns | The authoritative 1-minute ticker store and its verify and gap tools | Price history source | This branch reads the store through `snapshots.py` (read-only) and never writes to it. |

## Rules this branch follows
1. Own paths only: `engines/valuation/**` and `research/models/**` (B04 write scope in `orchestration/sparks.json`).
2. Evidence classes on every number: verified fact, issuer claim, secondary report, assumption, scenario output.
3. Price data comes from the `_PATTERNS` snapshot store; estimates and guidance carry source and date in `estimates.csv` and `guidance.csv`.
4. No claim of integration until merged and CI is green on main.
