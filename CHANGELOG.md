# Changelog

## 0.3.0 — 2026-10-16
- Adopt USD as the mandatory reporting currency across entity, NAV, traversal and relationship outputs.
- Persist 326 JPYUSD historical daily FX observations; retain original-currency and conversion metadata.
- Translate existing June 30 SFTBY historical NAV reference to USD with date-matched FX.
- Add deterministic SFTBY daily 5/20/60/200-session and partial-session intraday zoom report.
- Document missing 9984.T market history and the incomplete underlying holdings registry; do not claim cross-market reconciliation is complete.
- Pending: verify CI and replay, holdings source reconciliation, incremental market-data refresh.

# Changelog

## 0.2.0 — 2026-10-16
- Persist 262 completed daily Massive OHLCV observations each for AAOI, CRWV and SFTBY in independent per-ticker `history.jsonl`.
- Add `history.meta.json` with provider, adjustment and positional schema metadata.
- Add contextual entity, events and relationships JSON skeletons without speculative data.
- Add versioned schemas for all four canonical record types.
- Add automated validation script and GitHub Actions workflow; workflow execution not yet verified.
- Mark architecture as experimental/partially implemented; valuation, traversal and economic engines remain pending.

# Changelog

## 0.1.0 — 2026-10-16
- Define BASKET purpose, weighted objectives, assessment and roadmap.
- Lock per-entity history.jsonl and contextual entity/relationships/events JSON.
- Add shared architecture validation schema and version policy.

Status: design, not implemented or backtested.
