# B06 — Self-relative historical state (research only)

Issue [#154](https://github.com/whiterosecoffee/_BASKET/issues/154) · Spark B06 · branch `work/154-self-relative-historical-state`

## Decision and scope (2026-11-03)
- Primary objective: **incremental explanatory/discriminative information** over existing B06 traversal primitives; do not assume trading alpha.
- Lookback: **recent 200–500 completed daily sessions** with the exact eligible sample size reported. A 200-session MA needs 200 completed sessions to exist; a 200D distance percentile additionally needs historical post-warmup observations. Never fabricate the early percentile or infer 500 sessions exist.
- Handoff at **research specification** with B00 reconciliation; no engine/runtime/CI/shared-schema writes and no claims of successful numerical backtests.
- Owner/write boundary: **only** `research/traversal/self_relative_state/**`. Daily ticker observations are read from B00-approved B02 canonical resolver when available, not copied into B06.
- Proposed interface is an experimental research shape, not an approved cross-domain schema.
- This directory now includes research documents, a nonproduction reference calculator and synthetic conformance tests. No material here is a live trading recommendation. The synthetic fixtures do not establish historical classification lift.

## Live draft PR collision review (read-only inspection)
| Source | Verified feature / claim | Avoid duplication |
|---|---|---|
| [B06 PR #109](https://github.com/whiterosecoffee/_BASKET/pull/109), `engines/traversal/metrics.py` | Completed-bar intraday observed 5/15/60/390m ranges, velocity, turnover, directional/path efficiency, explicit missing estimates | Do not reimplement these intraday primitives |
| [B06 PR #150](https://github.com/whiterosecoffee/_BASKET/pull/150), `engines/traversal/market_geometry/core.py` | Synchronized 1/5/15/30/60m returns, range position, velocity/acceleration and QQQ/SPY, RSP/SPY, SMH/QQQ, IWM/SPY ratio changes; explicit `range_start` | Do not reimplement synchronized intraday geometry or invent sector-beta inference |
| [B06 PR #145](https://github.com/whiterosecoffee/_BASKET/pull/145), `research/traversal/october_2026_compression_stress/PRIOR_ART_SIGNAL_MODEL.md` | Multi-scale traversal ontology, turnover, volume acceptance proxy caveats, regime/event provenance, falsification methods | Use its definitions; don't recreate a separate battle-zone ontology |
| [B17 PR #101](https://github.com/whiterosecoffee/_BASKET/pull/101) | Cross-ticker market-context and delta provider | Request standardized contextual residuals; no B06 edit to B17 |
| [B10 PR #99](https://github.com/whiterosecoffee/_BASKET/pull/99) | Completed-minute range event consumer, replay/poller within CRWV research domain | Do not fork state store, poller or freeze-band lifecycle |
| [B00 PR #147](https://github.com/whiterosecoffee/_BASKET/pull/147), [migration #148](https://github.com/whiterosecoffee/_BASKET/issues/148) | `_TICKERS` identity scopes proposed; data migration/resolver remains an integration gate | Never infer a scope folder contains migrated history |

## Proposed incremental dimensions
1. Daily price-to-10/30/200-session MA distance and MA slopes; cross-horizon disagreement; completed-session persistence.
2. ATR or realized-volatility normalized distance, and rolling, **past-only** empirical rank of that distance, with missingness.
3. Conditioned historical event cohorts (MA proximity, approach speed, persistent trend, volatility/market state) and distribution of *subsequent* realized paths; descriptive retrospective research, not forecasts.
4. Comparison with B06 geometry/traversal and B17 context to quantify incremental discrimination, not to imply a 200D line is causal support.

## Ownership / release
B06 owns only this research subtree. B00 owns shared contracts/registry and resolver arbitration; B02 owns observations, corporate-action adjustments and point-in-time data; B17 owns market context; B07 owns outcome calibration; B01 owns independent integration validation. Existing handoffs take precedence: #148 for ticker migration, #93 for B07 ledger, #100 for B17 context. New cross-domain requirements must be added as targeted linked handoffs, not assumed permissions.

See [RESEARCH_CONTRACT.md](RESEARCH_CONTRACT.md), [VALIDATION_AND_HANDOFF.md](VALIDATION_AND_HANDOFF.md), [PAIRED_REPLAY.md](PAIRED_REPLAY.md), [IMPROVEMENT_ROADMAP.md](IMPROVEMENT_ROADMAP.md), [MATURATION_SCORECARD_AND_SEQUENCE.md](MATURATION_SCORECARD_AND_SEQUENCE.md), [reference_state.py](reference_state.py), [test_reference_state.py](test_reference_state.py) and [ORCHESTRATOR_HANDOFF.md](ORCHESTRATOR_HANDOFF.md).
