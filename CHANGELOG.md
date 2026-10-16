# Changelog

## Unreleased — v0.5.0 candidate (not shipped)
- Introduce worker task, resolution and GitHub evidence schemas plus offline B00 evaluator and negative tests; integration in B01 CI remains pending.
- Proposed independent conversation branching, domain ownership, handoff issues and 22 scoped launch sparks.
- Proposed complete ChatGPT Project Instructions in one maintained block and separate version tracks for core, orchestration, schemas, datasets, engines and reports.
- Add formal release manifest and evidence gates; do NOT raise the declared 0.4.1 baseline until validated and authorized.
- Pending: strict SFTBY relationships schema/data reconciliation, passing CI, PR review/merge and an authorized immutable release tag.

## 0.4.1 — 2026-10-16
- Correct TTD terminology to **Time to Die**: hard validity expiry for observations and computations.
- Add local-first, append-only JSONL ingestion and polling runtime with predetermined paths and source-adapter contracts.
- Add dependency-aware expiry, feed configuration, status reporting and unit tests.
- Feeds are disabled until live provider adapters and a persistent worker are configured; no claim of ongoing updates or validated CI.
- Clarify that dead records remain for replay but are never current NAV inputs.

## 0.4.0 — 2026-10-16
- Specify USDJPY as a first-class FX market entity with independent traversal and USD-first conversion.
- Define per-field TTD (Time to Die) expiration windows, provenance, stale/unavailable/conflicted states and a freshness evaluation module.
- Specify dynamic mark-to-market SFTBY NAV with FX decomposition by asset, debt, expenses, cash, hedges and maturity.
- Mark live FX and latest-trade access as unavailable under the tested Massive entitlement; do not claim live NAV.
- Require dated ownership/share counts, non-double-counted fund exposures and explicit provisional valuation flags.
- Pending: live provider, holdings reconciliation, working NAV calculation and validated TTD pipeline.

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
