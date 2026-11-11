# Market-context evidence and reproducible captures

Worker B17 #100. Scope is only `engines/composites/market_context/**` and this
subtree. No shared workflows, registries, market stores or traversal files changed.

`registry.working.json` contains 66 company research candidates from the exact
PR #18 registry commit, with QQQ/SMH separated as benchmarks. Main has only three
matching canonical public ticker entities; candidate membership is not presented
as authoritative main or personal holdings. PAYP remains unresolved and is
excluded from quote admission while retained in the denominator. Sector proxies
are heuristic mappings awaiting B00 review; diversified issuers can fit multiple
business groups and a proxy is not a revenue attribution.

## Fixtures

- `premarket.csv/json`: actual Massive response captured during the October 29
  premarket test, as-of 08:28:11 ET (individual price timestamps near 08:27).
- `midday.csv/json`: actual response at 12:38:48 ET, for the original subset.
- `basket.csv/json`: one subsequent all-universe Massive request. Capture cutoff
  derives from the maximum observed provider timestamp plus one second; first
  known capture bound is 12:45:48 ET. Source entitlement was not explicit.
- `midday-report.json`: retrospective research evaluation under the subsequently
  authored registry. Not a point-in-time strategy result.
- `basket-report.json`: provisional research evaluation, current capture versus
  the previous subset. Interval coverage remains low because adding a full quote
  universe now cannot fabricate earlier quotes for those names.

These static historical fixtures are not current prices. Every report states
coverage and null missing macro factors; full macro score is withheld. No figures
in a report should be treated as performance of the user's personal portfolio.

## Validation

Run the engine's unittest command from its README. Tests cover freshness, delayed
entitlement gates, stale trade bars despite fresh session updates, quote conflicts,
unknown symbols, full-universe denominators, mismatched baselines, no lookahead,
matched-universe deltas, rolling-window alignment, correction replay, duplicate
IDs, macro unit/expiry gates and growth-shock overrides. See `VALIDATION.md` for
actual run evidence and known limitations.
