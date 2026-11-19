# Feature design — synchronized SMH/SOXX forward-earnings comparison

**Owner:** B04. **Parent:** `OPTIMIZATION_PLAN.md`; **reference:** `MATURATION_ROADMAP.md`; **worker issue:** #126; **draft PR:** #127. **Version:** `etf-peer-compare@0.1.0`. Feature status: experimental, synthetic tests only. This module does not own market data, issuer holdings or consensus stores.

## Problem and reusable contract

A reported issuer P/E can differ across funds due to portfolio holdings, calculation definition, date, missing loss-making issuers, and cash/derivative handling. The calculation must NOT infer relative undervaluation from two unsynchronized published P/E numbers or treat the inverse P/E as standalone ETF operating EPS.

**Input:** `compare_funds(request)` in `compare_funds.py`.

- Required `schema: basket.etf_peer_comparison_input@1`.
- `as_of`, `holdings_effective_date`, `equity_market_cap_as_of`; two issuer-primary fund objects with `ticker=SMH` and `ticker=SOXX`, and identical declared price/holdings vintages.
- Every fund uses the existing `lookthrough.calculate` contract: exact weight normalization, explicit USD market caps, USD-normalized CY2027/CY2028 common net income, `available_at`, asset type, data kind and nonempty source manifest.
- Source class and `data_kind=verified_observation` are **upstream assertions**, not cryptographically verified by this module. Do not promote external claims to verified without an independent data-adapter/source audit.

**Output:** `basket.etf_peer_comparison_output@1`: independently guarded 2027 and 2028 earnings yields, P/E or null, estimate coverage, SMH-minus-SOXX earnings-yield difference, constituent-level attribution of the yield spread, descriptive lower-P/E indicator (only with complete positive earnings), source input SHA-256 and limitation disclosure. `peer_report.render_peer_markdown` produces a dated, marked readable report.

### Method

For each fund/year, the inherited economic formula is `EY = sum(weight_i * common_net_income_i / market_cap_i)`, including **negative earnings** with sign. Cash has an explicit **zero earnings-yield assumption**; derivatives and other unsupported holdings fail closed. `PE = 1/EY` only when all equity holdings are covered and aggregate EY is positive.

The yield spread is `EY_SMH - EY_SOXX`. For every security, its signed contribution is `SMH_weight*income/cap - SOXX_weight*income/cap` if present, zero on the absent side. Confirm contributions sum exactly to the spread. This is an earnings-yield decomposition, not a share-price-return attribution or an earnings-growth forecast.

### Tests and evidence

- `test_compare_funds.py`: 12 synthetic tests cover independent years, correct attribution, stale/mismatched declared date, estimate lookahead, incomplete data, currency, source class, duplicate funds, deterministic hash.
- `test_peer_report.py`: 3 synthetic tests cover report labeling, missing P/E and incompatible contract.
- `test_peer_cli.py`: 2 executable CLI tests against the pinned synthetic JSON fixture.
- A locally constructed equivalent using the same comparator and a reduced lookthrough stand-in passed **17/17** on 2026-11-19. This is **not** full checked-out branch execution; PR #127 exact-head B01 test gate #129 must rerun all previous 66 tests plus these new 17.

### Known limitations and falsifiers

- Strictly equal declared holdings effective date and market-cap timestamp is a first-pass conservative contract; real issuer holdings often publish at different times, so B00/B02 must approve an evidence-backed temporal alignment rule before relaxing it.
- No proof that individual market caps were actually sampled at the declared timestamp. The approved upstream snapshot must guarantee per-constituent vintage, currency, ADR share ratio, dilution and source hash.
- No source-verified 2027/2028 consensus available in this module, no ETF actual EPS/share calculation, no expenses, tracking, distributions, cash interest, derivative hedges or fund-owned-share reconciliation.
- Missing estimates in either fund suppress the comparative winner for that year. A lower multiple does **not** identify the risk-adjusted opportunity; that requires B04 risk/scenario engine plus historical calibrated evidence.
- SMH October 30, 2026 historical return attribution remains the separate unverified gate, not equivalent to this forward-earnings spread.

## Next steps and ownership

1. B01 #129: execute all B04 tests on exact latest PR #127 head, record CI run URL, test count and failures; existing previous-head 66-test acceptance is preserved as historical evidence.
2. B00 #136 + #128: confirm authoritative issuer ETF holdings source, temporal alignment and consensus estimate owner under existing _TICKERS migration. No new feed/registry.
3. B02: provide synchronized source-verified market-cap snapshot, closes, FX and effective date; B03: reported net earnings/cross-check, with external consensus provenance separately controlled.
4. B04: adapt pure `compare_funds` to approved versioned adapters, then create an actual 2027/2028 comparison with explicit coverage, and extend to other ETFs/optimized companies only after parity.
5. B07: independently validate walk-forward historical signal and actual downside risk before any risk-adjusted winner.

**Exit gate:** Real issuer-date holdings reconcile, source-instrument effective/available times verified, 2027 and 2028 coverage sufficient, tests accepted, independent risk comparison. No merge or release without user authorization.

### Working entry point

Run `python compare_funds.py smh_soxx.synthetic.json --format markdown` from the owned module directory. The reproducible source fixture is explicitly synthetic; the generated figures are *not* actual SMH/SOXX earnings or valuation. Other consumers may call `compare_funds(request)` and `render_peer_markdown(output)` directly. Do not duplicate inputs or adapter outputs in any other repository location.
