# ETF forward valuation — B04 offline component (experimental)

Engine version: `etf-forward@0.1.0`. Output contract: `basket.etf_forward_output@1` (module-local candidate, not approved shared schema). This is **not** a live ETF ranking or issuer reconciliation.

Run: `cd engines/valuation/etf_forward && python -m unittest -v test_engine.py`

CLI: `python engine.py input.json --output result.json`. Import `analyze(data)` and `sensitivity(yield, earnings_revisions, multiple_factors)`.

Inputs require timestamped holdings and calendarized USD net-income estimates available no later than `as_of`; weights must sum to 1 including cash. Estimates after as-of are rejected. Positive, complete aggregated earnings yield yields reciprocal P/E; negative aggregate earnings or partial coverage suppresses P/E. Sensitivity decomposes conditional price change into earnings, multiple and interaction terms. Canonical sorted input JSON hashes for repeatability.

**Limitations / blocked acceptance**: no entitlement-backed holdings ingestion, issuer holdings snapshots, share-class/ADR FX conversions, fiscal calendarization, historical point-in-time revisions, real issuer FY2027/2028 consensus, fund-owned-share reconciliation, fees/tracking, forward growth, historical SMH October 30 attribution or actual stress-risk calibration. These MUST NOT be assumed from this prototype. Foreign reporting and non-USD inputs fail closed. No actual ETF or constituent return, earnings multiple, or opportunity claim is supported.

Next: request B02/B03 source-adapter interface and B01 exact-head execution; B00 approval for any cross-domain schema. No other spark's files may be changed.

## Incremental maturation — dual-horizon economic look-through

`lookthrough.py` provides `calculate(snapshot)` with a separate module-local candidate output `basket.etf_lookthrough@1`. It does **not** replace the legacy `engine.analyze` contract; downstream adapters must choose the correct version explicitly until B00 approves schema evolution. Only `equity` and explicitly USD `cash` are supported; derivative/negative-asset positions fail closed. The cash assumption is **zero earnings yield**, not a claim about the actual fund's interest income. Loss-making equity earnings remain signed. Full equity estimate coverage and positive aggregate fund yield are required before emitting P/E. Individual-year coverage and P/E validity are distinct.

Minimal input:
```json
{
  "as_of":"2026-10-30T20:00:00Z",
  "data_kind":"synthetic_test",
  "source_manifest":[{"id":"toy-only"}],
  "holdings_available_at":"2026-10-29T20:00:00Z",
  "holdings":[
    {"id":"EXAMPLE","asset_type":"equity","available_at":"2026-10-29T20:00:00Z","weight":"0.9","equity_currency":"USD","market_cap_usd":"100","estimates":{
      "2027":{"calendar_year":2027,"available_at":"2026-10-29T20:00:00Z","currency":"USD","net_income_usd":"10"},
      "2028":{"calendar_year":2028,"available_at":"2026-10-29T20:00:00Z","currency":"USD","net_income_usd":"15"}
    }},
    {"id":"CASH","asset_type":"cash","available_at":"2026-10-29T20:00:00Z","currency":"USD","weight":"0.1"}
  ]
}
```

To run **all** B04 domain unit tests:
```bash
cd engines/valuation/etf_forward
python -m unittest discover -p 'test_*.py' -v
```

The source manifest is passed through and hashed, **not cryptographically verified** against issuer documents. An upstream approved adapter must establish issuer provenance, original currency/FX pair/date, share classes/ADR ratio, available/ingested times and TTD. Therefore `verified_observation` is a **caller assertion**, not independent proof. Direct fund ownership/share-unit reconciliation, derivatives, expenses, dividends, dynamic rebalancing, risk-adjusted winner selection and real 2027/2028 consensus integration remain open. New local `test_lookthrough.py` checks 11 negative/correctness cases; local success is **not** SHA-matched independent GitHub CI.

## Period-aware conditional price return (2027 versus 2028)

`return_bridge.py` adds the separately versioned `bridge(earnings_change, multiple_factor, horizon_years, annual_expense_rate, round_trip_cost, return_basis)`. It derives gross conditional price return from earnings change × multiple factor, decomposes the interaction, compounds an explicitly **annual** expense rate for the selected number of years, and deducts round-trip trading costs **once**. It rejects `return_basis="observed_etf_nav"`: observed fund prices already embed expenses, so a second fee deduction would double-count them. The output is **share-price appreciation, not total return**; no dividends, withholding taxes, taxes on gains, leverage financing, slippage uncertainty or rebalancing are included.

`test_return_bridge.py` contains ten tests. The new look-through and bridge modules passed **21/21 locally** on 2026-11-04. Independent complete-suite test execution at current GitHub head is still pending B01 #129. The pre-existing `upside.py` and `portfolio.py` remain **legacy experimental contracts** and are not automatically upgraded by adding the new bridge; integrations must explicitly select the new version to avoid silent reinterpretation. The return bridge's net-price factor is a model sensitivity, not a validated ETF forecast.

## SMH/SOXX peer comparison (experimental)

New read-only `compare_funds.compare_funds(request)` composes the existing `lookthrough.calculate` and returns `basket.etf_peer_comparison_output@1`. It requires:

- `schema="basket.etf_peer_comparison_input@1"`; common `as_of`, `holdings_effective_date`, `equity_market_cap_as_of`.
- Exactly two fund snapshots, SMH and SOXX, each with issuer-primary (upstream-asserted) holdings provenance and matching declared dates, a nonempty source manifest, and complete USD-normalized inputs for each constituent.
- Separate calendarized 2027/2028 net income estimates. A year's comparison is **unrankable** if either fund lacks complete positive aggregate earnings yield.
- The spread decomposes as `EY_SMH - EY_SOXX = sum_ticker(contribution_SMH - contribution_SOXX)`; it is **not** stock-return attribution.

`peer_report.render_peer_markdown(result)` produces a date-labeled, synthetic-explicit comparison report. A lower P/E is not a risk-adjusted winner. This component does not claim real ETF EPS, estimate currency conversion, synchronized true source market caps, external provider entitlement, issuer NAV reconciliation or current 2027/2028 valuations.

Run tests via `cd engines/valuation/etf_forward && python -m unittest discover -p 'test_*.py' -v`. New modules `test_compare_funds.py` (12 cases), `test_peer_report.py` (3 cases), and `test_peer_cli.py` (2 cases) were locally executed against a reconstructed lookthrough dependency; **17/17 pass**, but the exact GitHub-head suite requires B01 #129 acceptance. See `feature-design-peer-comparison.md` and `state.json`. Existing 66 tests were previously run independently at the *previous* head; those results must not be attributed to new code.

Follow #128 for authoritative issuer/consensus data ownership and #136 for B00 orchestrator routing. No cross-domain writes or merges from B04.

### Reproducible CLI demonstration (synthetic, not live)

```bash
cd engines/valuation/etf_forward
python compare_funds.py smh_soxx.synthetic.json --format json --output /tmp/smh_soxx_demo.json
python compare_funds.py smh_soxx.synthetic.json --format markdown --output /tmp/smh_soxx_demo.md
```

The pinned `smh_soxx.synthetic.json` contains **toy values** that are not actual issuer holdings, EPS, market capitalizations or observed consensus. Do not distribute its P/E results as real ETF valuation. The Markdown output explicitly labels synthetic data and states no risk-adjusted winner. Independent B01 CI must execute all existing tests plus the 17 new peer/CLI cases on the current PR head.
