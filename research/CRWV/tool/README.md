# CRWV Operating Economics & Valuation Tool

B10 #86. Offline domain component, version `crwv-economics@0.1.0`. Writes only `research/CRWV/tool/**`. Source specification: #68 / PR #69, commit `29463811e8f77eac9d05b631fcb1c6190bf3f3ff`. Feed/traversal integration remains #70. Nothing here asserts current CRWV balances, targets or live operation.

## Run from repository root

Standard-library finance path; no installation, API keys, network or website required:

```bash
python -m unittest discover -s research/CRWV/tool/tests -v
python research/CRWV/tool/demo.py --output /tmp/crwv-economics-demo
python research/CRWV/tool/run.py \
  --input research/CRWV/tool/fixtures/snapshot.json \
  --config research/CRWV/tool/fixtures/base.json \
  --as-of 2026-10-27T14:30:00Z \
  --json-output /tmp/crwv-result.json \
  --text-output /tmp/crwv-result.txt \
  --history /tmp/crwv-valuation-history.jsonl \
  --reason 'Synthetic offline acceptance run'
```

For the explicitly unfunded case use `fixtures/unfunded-snapshot.json` and `fixtures/unfunded.json`. Month index 1 (December 2026 in the fixture) is the first gap. Negative cash and unpaid principal remain visible; equity issuance stays zero; all target indications are null. Later positive cash does not retroactively fund the gap. The plan's subsequent capacity/revenue are labeled conditional, not an executable funded build.

The demo produces **real calculated** JSON/text for slow/base/bull/unfunded cases, an append-only valuation ledger, a fixed-horizon revision bridge, accounting-life/earning-life/delay/benchmark sensitivities, and a mutually exclusive keep/upgrade illustration. All fixture economics are synthetic. `examples/` contains compact captured outputs; regenerate the full monthly outputs locally. Scenario weights are subjective labels and are not used as calibrated probabilities or combined into an asserted target.

## Implemented path

`model.evaluate(snapshot, scenario_config, as_of, horizons)` validates dated sources and economic units, builds monthly cohort billable IT MW and contract revenue, caps each old/new contract pool, schedules cash collections, runs each fixed/floating/hedged facility, pays explicit principal, exposes funding gaps, reconciles cash/debt and earnings, issues approved finite equity/SBC shares, and produces present plus 3/6/12/24-month valuation points and reverse valuation. It never calls a feed. Default fixtures forecast 120 months; shorter forecasts must still cover cohort earning life and disposal.

`model.analyze` is the partial-output facade: required-missing finance inputs yield null dependent groups and an explicit reason; independently valid market groups can still run. Source availability after the as-of cut or unknown publication time blocks dependent finance. Historical expiration does not erase evidence or make it current. Source and config content hashes identify each run. All monthly metrics inherit the result's `metric_metadata`; periods and instrument/cohort IDs identify their dependency subsets. A CLI run also records its implementation Git SHA; pure calls leave it null unless supplied explicitly.

Revenue/MW is cohort/contract-specific. Old fixed pricing is not reset to a new-vintage price unless an explicit scenario changes it. Contracted, energized, installed, accepted and billable power appear separately. Billing starts only after the declared readiness and contract start; utilization cannot exceed one. No guaranteed NVIDIA fleet utilization is invented.

Debt commitments are not drawn balances. Draws require approved conditions and opening unrestricted-cash headroom, and cannot exceed eligible undrawn capacity. Coupons are invariant to traded-yield shocks; benchmarks affect only floating unhedged amounts. Restricted project cash pays growth capex only. Cash interest, capitalized interest, expensed interest, principal and capex remain distinct. No automatic financing pass-through is assumed.

Cash/earnings reconciliation: pretax income = adjusted EBITDA - SBC - D&A - disposal losses - expensed interest - upfront financing fees. Cash flow adds back noncash D&A/SBC, pays capitalized cash interest, reconciles collections/receivables, then applies sustaining/growth capex, principal and explicit financing. Taxes are positive-income cash tax with no invented loss-carryforward benefit. The executable tests include hand-calculated results, not only output shape.

## Valuation convention

The primary DCF is a **finite runoff of the supplied cohort fleet with retained cash and terminal liquidation**. Cash stays in the business during the liquidity simulation, rather than being both paid as dividends and used to fund deployments. Every explicit debt draw/repayment, issue fee, equity issue and SBC share enters terminal cash/share counts. The final claim is unrestricted plus released restricted cash less outstanding final debt, divided by final diluted shares and discounted to the target date. Opening debt is not subtracted again after being repaid. This is a conservative finite-fleet scenario, not a perpetual CRWV going-concern valuation. No unmodeled terminal growth, replacement fleet, trade-in subsidy or reinvestment return is added. Terminal continuation is rejected until replacement-capital contracts exist. The declared terminal-growth parameter is reserved and has no effect in runoff mode.

A separate forward-12-month P/E comparison uses after-interest earnings and weighted diluted shares, with no second debt subtraction. Negative EPS suppresses the P/E indication; runoff DCF remains the alternate method if funding is feasible. Future target dates differ from financial forecast periods and as-of dates. Discounting uses monthly periods; the short stub from as-of to forecast start is approximated as zero. A curve is conditional value at future dates, not a predicted price path.

Reverse P/E solves one dimension at a time: required net income, annual revenue, billable IT MW, annual revenue/IT-MW, EBIT margin, allowable net interest and diluted shares. It does not pretend the quote identifies all assumptions simultaneously. Quote availability/expiry is gated independently; no quote means null reverse output while the operating model still runs.

## Lifecycle and revisions

Remaining accounting basis is depreciated prospectively under alternative remaining lives; accumulated depreciation is never reversed. Taxes can legitimately transmit depreciation changes into cash, so the depreciation-only cash-invariance test sets tax to zero. Earning life gates revenue separately; 7-versus-9-year sensitivities expose years 7–9 cash. Physical-unit vintage must come from the source, not A100 architecture age. Residual value is an explicit assumption, not an NVIDIA guarantee.

`model.lifecycle` compares mutually exclusive keep versus surrender/upgrade branches: remaining old-fleet cash/resale versus invoice less hypothetical credit, downtime and new-fleet cash. Old-fleet earnings and surrendered-asset credits cannot be collected together. Upgrade cash flows must already include power, useful-throughput, maintenance and financing opportunity costs; v1 does not infer those from chip names. Lifecycle comparison is a separate sensitivity, not silently injected into the operating forecast.

`history.append_record` retains exact original snapshots, configs, results, explicit revision reasons and separately supplied actuals, linked by hashes. Exclusive lock plus append/fsync prevents overwrite. `history.bridge` uses an ordered fixed-target decomposition, with residual interactions. Original forecasts remain intact. Automatic time-roll decomposition, forecast-error scoring and data-vintage alignment across different forecast starts remain future work; mismatched starts are rejected rather than compared as if equal.

## Market adapters and ownership

`market.factor_adapter` executes the existing `factor_tracker.py` from a caller-supplied local checkout only after verifying its expected SHA-256. Use the hash in `source-manifest.json` and a read-only checkout at the pinned source commit. Optional dependency: NumPy, required by that existing research implementation. `accept_attribution` checks prior-only training dates, as-of cutoff and contribution reconciliation. QQQ/NVDA remain jointly fitted; HYG/IEF/USO are diagnostics, not issuer credit or causal evidence.

`market.adapt_research_turnover` transforms the source research `raw_daily` without duplicating its dataset. Availability is an explicit caller input, never inferred from ingestion. `turnover` keeps regular/premarket/after-hours separate; reports 5/20/60-session windows, Oct 7 2026 anchor on XNAS, VWAP/notional, signed return/notional and gross traveled bar ranges. Missing windows stay missing. No unique-owner turnover, net flows, minute-bin density or within-bar touch ordering is invented. Debounced touches, first-passage denominators/censoring, held-out transition validation and execution-cost cycle measures remain B06/B07 via #70; adapters return null for these conclusions.

No upstream ingestion, shared schemas, shared valuation engine, CI workflows, runtime or persistent scheduling are modified. Shared finance-engine adoption belongs to B04; feed/traversal/runtime wiring stays owner-routed. Domain CI requires B01 integration; passing shared repository checks alone is not proof these tests ran.

## Explicit v1 limits

See [local contracts](contracts/README.md). Current reconciled balances, customer acceptance, prepayment/refund legal terms, hedge terms, leases, actual convertible exercises and full fleet ages are not established. Contract prepayment/refund accounting, convertibles and non-debt leases are unsupported and must be declared as such; the validator rejects declared unsupported features. The fixture does not stand in for them. Accounting is simplified GAAP-like arithmetic, not an audited statement model. Sustaining capex lacks asset commissioning/depreciation schedules. The full blueprint includes later measurement/calibration/integration gates beyond this first executable milestone.
