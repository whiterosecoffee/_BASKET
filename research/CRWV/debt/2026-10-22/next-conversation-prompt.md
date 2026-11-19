Build the CRWV Operating Economics & Valuation Tool inside whiterosecoffee/_BASKET.

This is an implementation conversation. Produce an executable component, not another research report or standalone app.

First read current main AGENTS.md, orchestration/sparks.json, orchestration/WORKER_PROTOCOL.md and relevant planner scopes. Inspect current issues, active PR changed-file ownership and dependencies. Create YOUR own issue and unique work/<issue-number>-crwv-functional-tool branch from latest main. Proposed exclusive writes: research/CRWV/tool/**, subject to collision checks. Do not reuse branch work/68-crwv-debt-stack-audit or edit its owned research/CRWV/debt/2026-10-22/** files.

Recover the source work from issue #68 and PR #69. Read functional-tool-blueprint.md and next-conversation-prompt.md in research/CRWV/debt/2026-10-22/ at PR #69's freshly retrieved head; those files may not be merged into main. Record the source commit SHA. Read existing debt registers, capacity-conversion.md, integrated-assessment.md, factor_tracker.py, october-turnover-velocity.json and capacity-scenarios.py. Preserve them as historical evidence. Reuse handoff #70 for market-feed/traversal integration; do not duplicate it.

Objective: one reproducible snapshot-to-analysis component that explains CRWV capacity, contracts, financing, cash, earnings, dilution and valuation through time, with market divergence and traversal outputs as separate modules.

Implement the first complete offline path:
dated local inputs -> billable capacity/revenue -> instrument-level funding waterfall -> earnings and dilution -> present/future valuation -> machine-readable JSON and concise human output.
Use explicit input/output contracts, source IDs, units, missing-data states, availability timestamps, hashes and method/config versions. Functions consume local upstream data; fetching and persistent scheduling stay with their owners.

Critical improvements:
1. Model capacity by cohort and month: contracted/energized/installed/accepted/billable are distinct. Annual revenue/MW uses equivalent power definitions and contract tenors. Reconcile backlog, RPO, later bookings and revenue without double-counting.
2. Model debt by instrument, drawn versus eligible undrawn availability, fees, hedges, amortization and restrictions. Do not reprice fixed coupons with market yields. Show the earliest funding gap and capacity consequences; never automatically fill deficits with costless or unlimited equity/debt.
3. Separate growth capex, sustaining capex, depreciation, cash/expensed/capitalized interest, principal, taxes and SBC. Build actual earnings-to-cash and dilution bridges. Audit the old scenario's assumed starting balances, uniform rate and equity plug; do not treat them as verified.
4. Separate GPU accounting life from earning life and resale/trade-in value. Model continued operation, replacement and hypothetical NVIDIA support as distinct choices. A100 architecture age is not physical-unit age. Do not assert an existing CRWV trade-in guarantee or assign unsupported probabilities.
5. Produce slow/base/bull sensitivities with visible assumptions; label any weights subjective unless calibrated. Show present fair value, 3/6/12/24-month conditional valuation, reverse valuation and changes versus earlier snapshots. Keep target date separate from forecast period and as-of date. Do not subtract debt twice or confuse adjusted margin targets with GAAP-like margins.
6. Adapt existing QQQ/NVDA jointly fitted attribution; HYG/IEF/USO are diagnostics. Residual is unexplained return, not proven issuer news. Later add AI peer controls and actual issuer-credit observations through owner contracts.
7. Preserve Oct7-anchored VWAP, turnover, price/volume velocity and session separation. Turnover is not unique holder replacement or net capital inflow. Traversal bands require defined touches, sample sizes, held-out validation and trading costs.

First milestone must run from a documented command and produce a real result. Test balance/cash conservation, source-date cuts, missing inputs, acceptance delays, fixed/floating shocks, dilution and depreciation-only changes versus genuine cash improvement. Show an unfunded scenario explicitly. Do not postpone offline work while waiting for live feeds.

Stay within ownership. Route shared valuation, schemas, ingestion, traversal, runtime and CI through their existing owners. Open a draft PR, record exact test results and exact-head CI status honestly, post the worker resolution, and never self-merge. Report what runs, what remains unverified and ONE next action.
